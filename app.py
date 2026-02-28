from flask import Flask, jsonify
import os

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/api/features')
def get_features():
    return jsonify({
        'status': 'success',
        'features': [
            '🚀 Backend is running',
            '⚡ Dynamic feature loading enabled',
            '🎨 Enhanced styling available'
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
