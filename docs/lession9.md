### Lession 9

# Message Queue - Receive

## Add Worker

Add Dependencies

```bash
poetry add celery
poetry add --group dev celery-types

```

```python
# cleaning/cleaning/worker.py
import logging
import os

from celery import Celery
from celery.signals import worker_process_init
from kombu import Exchange, Queue
from sqlmodel import Session

from cleaning.database import get_engine
from cleaning.models import Booking

logger = logging.getLogger(__name__)


@worker_process_init.connect(weak=False)
def init_celery_tracing(*args, **kwargs):
    logger.info("CeleryInstrumentator initializing")


amqp_url = os.getenv("AMQP_URL")
app = Celery("worker", broker=amqp_url)

app.conf.task_queues = (Queue("cleaning", Exchange("dispo"), routing_key="booking"),)
app.conf.task_routes = {"cleaning.celery_worker.*": "dispo"}


@app.task(name="booking.created")
def booking_created(data):
    logger.info(f"got message {data}")
    with Session(get_engine()) as db:
        booking = Booking(**data)
        db.add(booking)
        db.commit()

```

## Add Resources

### Start files

```sh
# cleaning/start-worker.sh
#!/bin/sh

set -e

. /venv/bin/activate

exec celery -A cleaning.worker \
  worker -l INFO -P solo

```

And similar for `start-debug-worker.sh` with adding `python -m debugpy --listen 0.0.0.0:5678 -m` between exec and clelery;


### Dockerfile

copy `api.Dockerfile` to `worker.Dockerfile` and set cmd to `start-worker.sh`

### Deployment Descriptor

```yaml
# deploy/cleaning_worker.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cleaning.worker
  labels:
    app: cleaning
spec:
  selector:
    matchLabels:
      app: cleaning
  template:
    metadata:
      labels:
        app: cleaning
    spec:
      containers:
        - name: cleaning-worker
          image: cleaning-worker
          env:
            - name: DATABASE_URL
              value: postgresql://cleaning:mysecretpassword@postgres/cleaning
            - name: AMQP_URL
              value: amqp://rabbit:mysecretpassword@rabbitmq:5672/
            - name: OTEL_EXPORTER_OTLP_ENDPOINT
              value: http://jaeger:4317
            - name: OTEL_SERVICE_NAME
              value: cleaning.worker
          command: ["./start-worker.sh"]
          resources:
            limits:
              memory: 256Mi
              cpu: 400m
```

### Tiltfile

```python
# tiltfile - add

docker_build(
    'cleaning-worker',
    context='./cleaning',
    dockerfile='./cleaning/api.Dockerfile',
    entrypoint=["./start-worker-debug.sh"],
    ignore=["**/__pycache__", ".pytest_cache", "**/*.pyc*"],
    live_update=[
        sync('./cleaning/cleaning', '/svc/cleaning'),
    ],
)

k8s_yaml('deploy/cleaning_worker.yaml')

k8s_resource(
    'cleaning',
    port_forwards=['5680:5678']
)
```

## Testing

After the worker has started successfully RabbitMQ should have registered a new queue named `cleaning` with the exchange `dispo`.

```bash
curl http://localhost:8000/api/v1/bookings/  -H "Content-Type: application/json" \
  -d '{"room_id": 1, "start": "2023-02-04", "end": "2023-02-06"}'

curl "http://localhost:8081/api/v1/days/?start=2023-02-01&end=2023-02-20" | jq
```

