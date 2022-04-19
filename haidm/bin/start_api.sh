#!/bin/bash
set -e

export HAIDM_SETTINGS=config.py

cd haidm
gunicorn --reload -c gunicorn.conf.py haidm:app
