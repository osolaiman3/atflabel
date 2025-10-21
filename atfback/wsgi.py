"""
WSGI entry point for the ATF Label Application
This file is used by production WSGI servers (Gunicorn, uWSGI, etc.)
"""
import sys
import os

# Add src directory to Python path so we can import server module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the Flask app from server.py
from server import app

# This is the WSGI application object that servers will use
if __name__ == "__main__":
    # This allows running with: python wsgi.py (for testing)
    # But production uses: gunicorn wsgi:app
    port = int(os.environ.get('PORT', 10000))
    app.run(port=port)
