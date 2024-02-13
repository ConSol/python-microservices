#!/bin/sh

set -e

. /venv/bin/activate

exec celery -A cleaning.worker worker

