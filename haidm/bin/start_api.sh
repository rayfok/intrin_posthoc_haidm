#!/bin/bash
set -e

export HAIDM_SETTINGS=config.py

gunicorn --reload -c gunicorn.conf.py haidm:app
