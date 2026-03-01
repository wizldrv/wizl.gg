from flask import Flask, render_template, jsonify
import os

app = Flask(__name__, static_folder='static', static_url_path='', template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

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
    # Production: debug=False, host configured for shared hosting
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='127.0.0.1', port=5000)
