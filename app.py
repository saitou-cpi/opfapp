from flask import Flask, request, jsonify, render_template
from controllers.optimal_parameter_finder import process_ticker, validate_parameters
from models.database import check_ticker_symbol

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize():
    ticker_symbol = request.form['ticker']
    initial_capital = request.form.get('initial_capital', type=int)
    if not ticker_symbol or not initial_capital:
        return jsonify({"error": "Ticker symbol and Initial capital are required"}), 400

    if not check_ticker_symbol(ticker_symbol):
        return jsonify({"error": "Ticker symbol not found in the database"}), 400

    result = process_ticker(ticker_symbol, initial_capital)
    if not result['trades_executed']:
        return jsonify({"error": "売買不成立"}), 400

    return jsonify(result)

@app.route('/validate', methods=['POST'])
def validate():
    ticker_symbol = request.form['ticker']
    upper_limit = request.form.get('upper_limit', type=float)
    lower_limit = request.form.get('lower_limit', type=float)
    initial_capital = request.form.get('initial_capital', type=int)

    if not all([ticker_symbol, upper_limit, lower_limit, initial_capital]):
        return jsonify({"error": "All parameters are required for validation"}), 400

    try:
        validation_result = validate_parameters(ticker_symbol, upper_limit, lower_limit, initial_capital)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(validation_result)

@app.route('/help')
def help():
    return render_template('helppage.html')

if __name__ == '__main__':
    app.run(debug=True)
