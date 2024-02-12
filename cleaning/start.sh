#!/bin/sh

set -e

. /venv/bin/activate

python -m cleaning.database

exec uvicorn \
  --host 0.0.0.0 \
  --log-config=log_conf.yaml \
  cleaning.main:app
