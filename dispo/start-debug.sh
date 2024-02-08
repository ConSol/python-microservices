#!/bin/sh

set -e

. /venv/bin/activate

python -m dispo.database

exec python \
  -m debugpy --listen 0.0.0.0:5678 \
  -m uvicorn \
  --host 0.0.0.0 \
  --log-config=log_conf.yaml \
  --reload \
  dispo.main:app
