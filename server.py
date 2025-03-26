from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
from datetime import datetime, timedelta
import pandas as pd
import json
import os
from cb_backtest.batch import BatchRunner
from cb_backtest.engine import FactorEngine
from cb_backtest.eval import evaluate_performance

app = Flask(__name__)

# Update CORS configuration
cors = CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173"],  # Your React app's URL
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
        "supports_credentials": True
    }
})

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# Handle OPTIONS requests explicitly
@app.route('/', methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path=None):
    return jsonify({}), 200

# MongoDB Configuration
app.config['MONGO_URI'] = 'mongodb://localhost:27017/monterey'
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
mongo = PyMongo(app)

# Configure your data paths here
CB_DATA_PATH = "path/to/your/cb_data.pq"
INDEX_DATA_PATH = "path/to/your/index.pq"

# Token verification decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = mongo.db.users.find_one({'username': data['username']})
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    
    # Check if user already exists
    if mongo.db.users.find_one({'username': data['username']}):
        return jsonify({'message': 'Username already exists'}), 400
    
    if mongo.db.users.find_one({'email': data['email']}):
        return jsonify({'message': 'Email already exists'}), 400
    
    # Hash the password
    hashed_password = generate_password_hash(data['password'])
    
    # Create new user
    new_user = {
        'username': data['username'],
        'email': data['email'],
        'password': hashed_password,
        'created_at': datetime.utcnow()
    }
    
    mongo.db.users.insert_one(new_user)
    
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    
    user = mongo.db.users.find_one({'username': data['username']})
    
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Generate JWT token
    token = jwt.encode({
        'username': user['username'],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, app.config['SECRET_KEY'])
    
    return jsonify({
        'token': token,
        'username': user['username']
    })

def load_and_filter_data(start_date, end_date):
    """Load and filter data based on date range"""
    df = pd.read_parquet(CB_DATA_PATH)
    index_df = pd.read_parquet(INDEX_DATA_PATH)
    
    df = df.loc[(df.index.get_level_values('trade_date') >= start_date) &
                (df.index.get_level_values('trade_date') <= end_date)].copy()
    
    index_df = index_df.loc[(index_df.index >= start_date) & 
                           (index_df.index <= end_date)].copy()
    
    return df, index_df

@app.route('/api/backtest', methods=['POST'])
@token_required
def run_backtest(current_user):
    try:
        # Get JSON data from request
        config = request.json
        
        if not config:
            return jsonify({"error": "No configuration provided"}), 400

        # Extract dates
        start_date = config['data']['start_date']
        end_date = config['data']['end_date']

        # Load and filter data
        df, index_df = load_and_filter_data(start_date, end_date)

        # Calculate factors
        engine = FactorEngine(df)
        df_with_factors = engine.compute_all_factors()

        # Initialize filter field
        df_with_factors['filter'] = False

        # Create output directory if it doesn't exist
        os.makedirs('result', exist_ok=True)

        # Run backtest
        runner = BatchRunner(df_with_factors, index_df)
        results = runner.run_all(config['strategies'], config['output_path'])

        # Calculate performance metrics
        performance_metrics = {}
        for name, result_df in results.items():
            metrics = evaluate_performance(result_df)
            performance_metrics[name] = metrics

        # Save backtest history to MongoDB
        backtest_history = {
            'user_id': str(current_user['_id']),
            'config': config,
            'performance_metrics': performance_metrics,
            'created_at': datetime.utcnow()
        }
        mongo.db.backtest_history.insert_one(backtest_history)

        return jsonify({
            "status": "success",
            "message": "Backtest completed successfully",
            "output_path": config['output_path'],
            "performance": performance_metrics
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.errorhandler(Exception)
def handle_error(error):
    status_code = 500
    if hasattr(error, 'code'):
        status_code = error.code
    
    response = jsonify({
        'error': str(error),
        'status_code': status_code
    })
    
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response, status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 
