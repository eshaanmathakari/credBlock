import sys
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import time

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
sys.path.insert(0, backend_path)

from credit_scorer import DeFiCreditScorer

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')  # This will load the front-end page

# API endpoint to calculate credit score (POST)
@app.route('/get_score', methods=['POST'])
def get_score():
    try:
        wallet = request.form['wallet']
        pool = request.form.get('pool', '0xA1b2C3d4E5f678901234567890abcdef12345678')  # Default pool address
        
        # Use the proper backend credit scorer
        scorer = DeFiCreditScorer(lending_pool_addr=pool, abi_path=os.path.join(backend_path, 'yei-pool.json'))
        result = scorer.calculate(wallet)  # Backend uses 'calculate' method
        
        # The backend returns a CreditScore dataclass with the correct format
        response = {
            'wallet': result.wallet,
            'score': result.score,
            'risk': result.risk,
            'confidence': result.confidence,
            'factors': {name: f"{score:+d} points" for name, score in result.factors.items()},
            'timestamp': int(time.time())
        }
        
        return jsonify(response)
    
    except Exception as e:
        error_response = {
            'error': True,
            'message': f'Error calculating credit score: {str(e)}',
            'wallet': request.form.get('wallet', 'Unknown'),
            'score': 0,
            'risk': 'Error',
            'confidence': 0.0,
            'factors': {},
            'timestamp': int(time.time())
        }
        return jsonify(error_response), 500

# API endpoint to calculate credit score (GET) - for Chrome extension
@app.route('/score/<wallet>', methods=['GET'])
def get_score_get(wallet):
    try:
        pool = request.args.get('pool', '0xA1b2C3d4E5f678901234567890abcdef12345678')
        
        # Use the proper backend credit scorer
        scorer = DeFiCreditScorer(lending_pool_addr=pool, abi_path=os.path.join(backend_path, 'yei-pool.json'))
        result = scorer.calculate(wallet)
        
        response = {
            'wallet': result.wallet,
            'score': result.score,
            'risk': result.risk,
            'confidence': result.confidence,
            'factors': result.factors,
            'timestamp': int(time.time())
        }
        
        return jsonify(response)
    
    except Exception as e:
        error_response = {
            'error': True,
            'message': f'Error calculating credit score: {str(e)}',
            'wallet': wallet,
            'score': 0,
            'risk': 'Error',
            'confidence': 0.0,
            'factors': {},
            'timestamp': int(time.time())
        }
        return jsonify(error_response), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': int(time.time()),
        'version': '1.0.0'
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
