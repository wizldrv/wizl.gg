"""
GitHub Webhook Handler for automatic deployment.
This script receives GitHub webhooks and pulls the latest code.

Setup:
1. Place this in your production directory
2. Run it as a background service
3. Add webhook to GitHub repo pointing to: https://yourdomain.com/webhook
4. Use secret: your_secret_key_here
"""

from flask import Flask, request, jsonify
import subprocess
import os
import hmac
import hashlib
import json
from datetime import datetime

webhook_app = Flask(__name__)

# Configuration - change these on production server
WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET', 'your-secret-key-here')
REPO_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(REPO_PATH, 'deployment.log')

def log_deployment(message):
    """Log deployment events"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry)
    print(log_entry.strip())

def verify_webhook_signature(request_data, signature):
    """Verify GitHub webhook signature"""
    expected_signature = 'sha256=' + hmac.new(
        WEBHOOK_SECRET.encode(),
        request_data.getdata(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)

def pull_latest_code():
    """Pull latest code from GitHub"""
    try:
        os.chdir(REPO_PATH)
        result = subprocess.run(['git', 'pull', 'origin', 'main'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            log_deployment(f"Git pull failed: {result.stderr}")
            return False, result.stderr
        
        log_deployment(f"Git pull successful: {result.stdout}")
        return True, result.stdout
    except Exception as e:
        log_deployment(f"Error pulling code: {str(e)}")
        return False, str(e)

def install_requirements():
    """Install/update Python requirements"""
    try:
        result = subprocess.run(['pip', 'install', '-r', 'requirements.txt'],
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            log_deployment(f"Requirements install failed: {result.stderr}")
            return False, result.stderr
        
        log_deployment(f"Requirements updated")
        return True, result.stdout
    except Exception as e:
        log_deployment(f"Error installing requirements: {str(e)}")
        return False, str(e)

def restart_app():
    """Restart Flask application"""
    try:
        # For production, you might use systemctl, supervisord, or other process managers
        # This is a placeholder - adjust based on your hosting setup
        log_deployment("Deployment completed - restart your app manually or via your hosting control panel")
        return True, "Restart signal sent"
    except Exception as e:
        log_deployment(f"Error restarting app: {str(e)}")
        return False, str(e)

@webhook_app.route('/webhook', methods=['POST'])
def github_webhook():
    """Handle GitHub webhook"""
    
    # Verify webhook signature
    signature = request.headers.get('X-Hub-Signature-256', '')
    if WEBHOOK_SECRET != 'your-secret-key-here':
        if not verify_webhook_signature(request, signature):
            log_deployment(f"Invalid webhook signature")
            return jsonify({'error': 'Invalid signature'}), 401
    
    try:
        payload = request.get_json()
        
        # Only deploy on push to main branch
        if payload.get('ref') != 'refs/heads/main':
            return jsonify({'message': 'Ignoring non-main branch'}), 200
        
        log_deployment(f"Webhook received from {payload.get('repository', {}).get('full_name')}")
        
        # Pull latest code
        success, message = pull_latest_code()
        if not success:
            return jsonify({'error': 'Failed to pull code', 'details': message}), 500
        
        # Install requirements
        success, message = install_requirements()
        if not success:
            return jsonify({'error': 'Failed to install requirements', 'details': message}), 500
        
        # Restart app
        success, message = restart_app()
        
        log_deployment("Deployment successful!")
        return jsonify({
            'status': 'success',
            'message': 'Deployment triggered successfully',
            'details': message
        }), 200
        
    except Exception as e:
        log_deployment(f"Webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    log_deployment("Webhook listener started")
    webhook_app.run(host='127.0.0.1', port=5001, debug=False)
