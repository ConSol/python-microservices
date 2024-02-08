#!/bin/sh

set -e

. /venv/bin/activate

python -m dispo.database

exec uvicorn \
  --host 0.0.0.0 \
  --log-config=log_conf.yaml \
  dispo.main:app
