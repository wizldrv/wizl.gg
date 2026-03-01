"""
WSGI entry point for production deployment on Namecheap shared hosting.
Used with gunicorn or other WSGI servers.
"""
from app import app

if __name__ == "__main__":
    app.run()
