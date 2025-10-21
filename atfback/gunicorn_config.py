# Gunicorn Configuration File for ATF Label Application
# Usage: gunicorn -c gunicorn_config.py wsgi:app

import multiprocessing
import os

# Server socket
bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:10000')
backlog = 2048

# Worker processes
workers = os.environ.get('GUNICORN_WORKERS', 2)
worker_class = 'sync'  # Use sync worker for Flask (suitable for most cases)
worker_connections = 1000
timeout = os.environ.get('GUNICORN_TIMEOUT', 120)  # 2 minutes for OCR processing
keepalive = 2

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = os.environ.get('GUNICORN_LOGLEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None
ssl_version = None
cert_reqs = 0
ca_certs = None
suppress_ragged_eof = True
do_handshake_on_connect = False
preload_app = False

# Application
paste = None
env = os.environ.copy()
raw_env = []

# Process naming
proc_name = 'atflabel'

# Server hooks
def on_starting(server):
    """Called when Gunicorn server is started"""
    print("\n" + "="*60)
    print("ATF Label WSGI Server Starting")
    print(f"Workers: {server.cfg.workers}")
    print(f"Timeout: {server.cfg.timeout}s")
    print("="*60 + "\n")

def when_ready(server):
    """Called when Gunicorn is ready to accept requests"""
    print("\n" + "="*60)
    print("ATF Label Server Ready")
    print("="*60 + "\n")
