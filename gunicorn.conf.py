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
# workers = 1
workers = multiprocessing.cpu_count() * 2 + 1

timeout = 3 * 60  # 3 minutes
keepalive = 24 * 60 * 60  # 1 day

capture_output = True

# connect to xbox live
main.authenticate()
