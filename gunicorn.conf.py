# run with 'gunicorn -c gunicorn.conf.py server:app'

import os
import multiprocessing

import main

loglevel = 'info'
errorlog = "-"
# uncomment to log every request / access
# accesslog = "-"


port = os.getenv("PORT") or 5000
bind = '0.0.0.0:' + str(port)
workers = 1
# 1 worker for now because of reauthing issues
# workers = multiprocessing.cpu_count() * 2 + 1

timeout = 3 * 60  # 3 minutes
keepalive = 24 * 60 * 60  # 1 day

capture_output = True
enable_stdio_inheritance = True

# connect to xbox live
main.authenticate()
