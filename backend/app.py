from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from portfolio import PortfolioSimulator
import os

app = Flask(__name__)
CORS(app)

simulator = PortfolioSimulator()

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'Portfolio Simulator API is running'})

@app.route('/api/generate', methods=['POST'])
def generate_portfolio():
    try:
        data = request.get_json()
        strategy = data.get('strategy', 'equal_weight')
        
        if strategy not in ['equal_weight', 'momentum', 'value']:
            return jsonify({'error': 'Invalid strategy'}), 400
        
        portfolio_data, filename = simulator.run_portfolio(strategy)
        
        if portfolio_data is None:
            return jsonify({'error': 'Failed to generate portfolio. Check API key.'}), 500
        
        return jsonify({
            'success': True,
            'strategy': strategy,
            'portfolio': portfolio_data,
            'total_stocks': len(portfolio_data),
            'filename': filename,
            'total_value': sum([stock['actual_position'] for stock in portfolio_data])
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)