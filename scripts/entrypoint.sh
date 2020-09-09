#!/bin/sh

set -e

python manage.py collectstatic --noinput

# Command that runs the app using uWSGI
uwsgi --socket :8000 --master --enable-threads --module thr.wsgi