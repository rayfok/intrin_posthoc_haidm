import os
import time

bind = "0.0.0.0:8878"
workers = os.environ.get('WORKERS', 4)
loglevel = os.environ.get('LOG_LEVEL', 'info')
accesslog = f'logs/gunicorn-{time.time()}.log'
preload = True

def post_request(worker, req, environ, resp):
    worker.log.info(f'{req.method} {req.path}?{req.query} {resp.status}')
