#!/bin/sh -e

python /cap/wsgi.py &

export C_FORCE_ROOT="true"
cd /cap
celery -A app.celery worker -l info
