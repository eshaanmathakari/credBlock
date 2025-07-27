from flask import Flask, render_template, request, jsonify
from credit_scorer import DeFiCreditScorer  # Assuming your scoring logic is in 'credit_scorer.py'

app = Flask(__name__)

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')  # This will load the front-end page

# API endpoint to calculate credit score
@app.route('/get_score', methods=['POST'])
def get_score():
    wallet = request.form['wallet']
    pool = request.form.get('pool', '0xA1b2C3d4E5f678901234567890abcdef12345678')  # Default pool address
    
    scorer = DeFiCreditScorer(lending_pool_addr=pool)
    result = scorer.calculate_credit_score(wallet)

    response = {
        'wallet': result.wallet,
        'score': result.score,
        'risk': result.risk,
        'factors': result.factors
    }
    
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
