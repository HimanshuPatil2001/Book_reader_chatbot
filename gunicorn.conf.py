# Gunicorn configuration file for production deployment
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Memory management
worker_tmp_dir = '/dev/shm'
max_requests_jitter = 50
graceful_timeout = 30
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'book_reader_chatbot'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Timeouts
timeout = 120
keepalive = 2
