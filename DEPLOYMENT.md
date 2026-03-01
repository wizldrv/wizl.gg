# Deployment Guide

This guide explains how to deploy your Flask app to Namecheap shared hosting with automatic GitHub webhook deployment.

## Prerequisites

- GitHub account with your repo
- Namecheap hosting account (wizlpqif)
- FTP/SFTP access to your server
- Python 3.x installed on your server

## Deployment Steps

### 1. Upload Files to Namecheap Server

Since SSH isn't available, use FTP or your Namecheap file manager to upload:
- All Python files (app.py, wsgi.py, webhook.py)
- requirements.txt
- templates/ folder
- static/ folder

Target directory: `/home/wizlpqif/public_html/wizl/` or similar

### 2. Install Dependencies on Server

Via cPanel terminal or Python environment:
```bash
cd /home/wizlpqif/public_html/wizl/
pip install -r requirements.txt
```

### 3. Set Up Webhook Handler

The webhook handler receives GitHub push notifications and auto-deploys your code.

**Option A: Manual Execution (Testing)**
```bash
python webhook.py
```

**Option B: Background Service (Production)**

Create a startup script or use your hosting's process manager:
- cPanel's "Manage Python App"
- Or manual systemd/supervisord configuration

### 4. Configure GitHub Webhook

1. Go to your GitHub repo: `wizldrv/wizl.gg`
2. Settings → Webhooks → Add webhook
3. Fill in:
   - **Payload URL**: `https://yourdomain.com/webhook`
   - **Content type**: application/json
   - **Secret**: Generate a strong secret key
4. Events: Select "Push events" only
5. Click "Add webhook"

### 5. Set Webhook Secret on Server

On your Namecheap server, set environment variable:
```bash
export GITHUB_WEBHOOK_SECRET="your-secret-from-github"
```

Or update the webhook.py file directly with your secret (less secure).

### 6. Test the Deployment

1. Push a change to GitHub main branch:
   ```bash
   git add .
   git commit -m "Test deployment"
   git push origin main
   ```

2. GitHub will send a webhook to your server
3. Check deployment log on server:
   ```bash
   cat /home/wizlpqif/public_html/wizl/deployment.log
   ```

4. Your app code will be updated!

## Troubleshooting

### Webhook Not Triggering
- Check GitHub repo webhook settings (Settings → Webhooks)
- Verify the Payload URL is correct and accessible
- Check "Recent Deliveries" tab in GitHub webhook settings

### Git Pull Fails
- Verify SSH key is set up on GitHub for your account
- Or use HTTPS: `git config --global url."https://".insteadOf git://`

### Requirements Install Fails
- Ensure Python and pip are in PATH on server
- Some packages might need system libraries (install via cPanel)

## Manual Deployment (Without Webhook)

If webhook fails, manually pull changes:
```bash
cd /path/to/app
git pull origin main
pip install -r requirements.txt
# Restart your app via cPanel
```

## App Configuration

### Environment Variables

Set these on your Namecheap server:
- `FLASK_ENV=production` (disable debug mode)
- `GITHUB_WEBHOOK_SECRET=your-secret`

### Flask Configuration

The app runs on:
- Local: `http://127.0.0.1:5000`
- Production: Use gunicorn or your hosting's Python app manager

**Start the app:**
```bash
gunicorn -w 4 -b 127.0.0.1:5000 wsgi:app
```

## Next Steps

1. Upload files to Namecheap via FTP
2. Install requirements on server
3. Set up GitHub webhook
4. Test by pushing code to GitHub
5. Monitor deployment.log for any issues

For help, check deployment.log for error messages!
