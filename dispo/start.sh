#!/bin/sh

set -e

. /venv/bin/activate

exec uvicorn \
  --host 0.0.0.0 \
  --log-config=log_conf.yaml \
  dispo.main:app
