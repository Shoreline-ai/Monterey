from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import json
import os
from cb_backtest.batch import BatchRunner
from cb_backtest.engine import FactorEngine
from cb_backtest.eval import evaluate_performance

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure your data paths here
CB_DATA_PATH = "path/to/your/cb_data.pq"
INDEX_DATA_PATH = "path/to/your/index.pq"

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
def run_backtest():
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

if __name__ == '__main__':
    app.run(debug=True, port=5000) 
