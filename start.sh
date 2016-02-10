#!/bin/sh -e

python /var/www/cap/wsgi.py &

export C_FORCE_ROOT="true"
cd /var/www/cap
celery -A app.celery worker -l info