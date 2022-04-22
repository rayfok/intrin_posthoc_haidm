import os
import time

bind = "127.0.0.1:8878"
workers = os.environ.get("WORKERS", 1)
loglevel = os.environ.get("LOG_LEVEL", "info")
errorlog = "logs/error-haidm.log"
accesslog = "logs/access-haidm.log"
preload = True
proc_name = "gunicorn-haidm"


def post_request(worker, req, _, resp):
    worker.log.info(f"{req.method} {req.path}?{req.query} {resp.status}")
