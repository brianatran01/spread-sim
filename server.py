from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

@app.route('/api/prices')
def get_prices():
    mode = request.args.get('mode', 'historical')  # 'historical' or 'live'
    
    try:
        if mode == 'live':
            # Last 5 trading days, 1-minute bars (most recent intraday data)
            cl = yf.Ticker("CL=F")
            ng = yf.Ticker("NG=F")
            cl_data = cl.history(period="5d", interval="1m")
            ng_data = ng.history(period="5d", interval="1m")
        else:
            # Historical: last 1 year of daily closes
            cl = yf.Ticker("CL=F")
            ng = yf.Ticker("NG=F")
            cl_data = cl.history(period="1y", interval="1d")
            ng_data = ng.history(period="1y", interval="1d")

        # Align on shared timestamps
        cl_series = cl_data['Close'].dropna()
        ng_series = ng_data['Close'].dropna()
        common = cl_series.index.intersection(ng_series.index)
        
        cl_aligned = cl_series[common].tolist()
        ng_aligned = ng_series[common].tolist()
        timestamps = [str(t)[:16] for t in common]

        return jsonify({
            'crude': cl_aligned,
            'natgas': ng_aligned,
            'timestamps': timestamps,
            'mode': mode,
            'count': len(common)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


import os
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5050)))
