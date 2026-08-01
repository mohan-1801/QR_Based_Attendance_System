import multiprocessing

# Gunicorn Production Configuration
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"
capture_output = True
enable_stdio_inheritance = True
