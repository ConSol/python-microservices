#!/bin/sh

set -e

. /venv/bin/activate

exec watchmedo auto-restart --directory=./ --pattern=*.py --recursive --  \
  python -m debugpy --listen 0.0.0.0:5678 -m \
  celery -A cleaning.worker \
  worker -l INFO -P solo

