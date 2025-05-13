from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
import os
import httpx
import logging
import yaml

env = os.getenv('ENV', 'local')

# Environment-specific configurations
ENV_CONFIG = {
    'local': {
        'cors_origins': ["http://localhost:5173"],
        'backtest_api_url': "http://127.0.0.1:8000/backtest",
        'log_file': "app.log",
        'mongo_url': "mongodb://localhost:27017"
    },
    'production': {
        'cors_origins': ["http://api.convertedbond.cn"],
        'backtest_api_url': "https://convertedbond.cn/backtest",
        'log_file': "/www/wwwlogs/os.convertedbond.cn.error.log",
        'mongo_url': "mongodb://localhost:27017"
    }
}

# Get current environment config
current_config = ENV_CONFIG[env]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(current_config['log_file']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('server')

logger.info(f"Current environment: {env}")

# Models
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class BacktestConfig(BaseModel):
    data: dict
    exclude_conditions: list = []
    score_factors: list = []
    weights: list = []
    hold_num: int = 5
    stop_profit: float = 0.03
    fee_rate: float = 0.002

# Initialize FastAPI app
app = FastAPI()
security = HTTPBearer()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=current_config['cors_origins'],
    # allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB configuration
db_client = AsyncIOMotorClient(current_config['mongo_url'])
db = db_client.monterey

# Configure data paths
CB_DATA_PATH = os.getenv('CB_DATA_PATH', '/Users/jinliangguo/dev/data/cb_data.pq')
INDEX_DATA_PATH = os.getenv('INDEX_DATA_PATH', '/Users/jinliangguo/dev/data/index.pq')

# Secret key for JWT
SECRET_KEY = "your-secret-key"  # Change this to a secure secret key
ALGORITHM = "HS256"

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        user = await db.users.find_one({"username": username})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    if await db.users.find_one({"username": user.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    if await db.users.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    hashed_password = generate_password_hash(user.password)
    new_user = {
        "username": user.username,
        "email": user.email,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    }
    
    await db.users.insert_one(new_user)
    return {"message": "User registered successfully"}

@app.post("/api/login")
async def login(user: UserLogin):
    db_user = await db.users.find_one({"username": user.username})
    if not db_user or not check_password_hash(db_user["password"], user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    token = jwt.encode(
        {
            "username": db_user["username"],
            "exp": datetime.utcnow() + timedelta(hours=24)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return {
        "token": token,
        "username": db_user["username"]
    }

@app.post("/api/backtest")
async def run_backtest(config: BacktestConfig, current_user: dict = Depends(get_current_user)):
    try:
        async with httpx.AsyncClient() as client:
            # Simplify the payload structure - remove the "request" wrapper
            payload = {
                "data": {
                    "start_date": config.data['start_date'],
                    "end_date": config.data['end_date']
                },
                "strategy": {
                    "exclude_conditions": config.exclude_conditions,
                    "score_factors": config.score_factors,
                    "weights": config.weights,
                    "hold_num": config.hold_num,
                    "stop_profit": config.stop_profit,
                    "fee_rate": config.fee_rate
                }
            }
            
            logger.info(f"Sending payload: {payload}")
            response = await client.post(
                current_config['backtest_api_url'],
                json=payload,
                timeout=30.0
            )

            # Check if the request was successful
            response.raise_for_status()
            result = x.json()

            # Create a properly structured response
            formatted_result = {
                "annual_return": result.get("annual_return", 0.0),
                "max_drawdown": result.get("max_drawdown", 0.0),
                "sharpe_ratio": result.get("sharpe_ratio", 0.0),
                "sortino_ratio": result.get("sortino_ratio", 0.0),
                "win_rate": result.get("win_rate", 0.0),
                "trade_count": result.get("trade_count", 0),
                "avg_hold_days": result.get("avg_hold_days", 0.0),
                "daily_returns": result.get("daily_returns", []),
                "positions": result.get("positions", {}),
                "trades": result.get("trades", [])
            }

            # Save backtest history to MongoDB
            backtest_history = {
                "user_id": str(current_user["_id"]),
                "config": config.dict(),
                "result": formatted_result,
                "created_at": datetime.utcnow()
            }
            await db.backtest_history.insert_one(backtest_history)

            return {
                "status": "success",
                "message": "Backtest completed successfully",
                "result": formatted_result
            }

    except httpx.HTTPError as e:
        logger.error(f"HTTP error occurred: {str(e)}")
        logger.error(f"Response content: {e.response.content if hasattr(e, 'response') else 'No response content'}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error calling backtest API: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Backtest error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001) 
