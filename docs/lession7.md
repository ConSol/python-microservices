### Lession 7

# Message Queue - Produce

We are using Celery for messaging and RabbitMQ as broker. The messages are send to an exchnage named `dispo`. Consumers will then subscribe to this exchange and will get their own queue. (pub-sub)


## Add Broker

```yaml
# deploy/rabbitmq.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rabbitmq
  labels:
    app: rabbitmq
spec:
  selector:
    matchLabels:
      app: rabbitmq
  template:
    metadata:
      labels:
        app: rabbitmq
    spec:
      containers:
        - name: rabbitmq
          image: rabbitmq:3-management
          ports:
            - containerPort: 15672
            - containerPort: 5672
          env:
            - name: RABBITMQ_DEFAULT_USER
              value: rabbit
            - name: RABBITMQ_DEFAULT_PASS
              value: mysecretpassword
          resources:
            limits:
              memory: 256Mi
              cpu: 400m
---
apiVersion: v1
kind: Service
metadata:
  name: rabbitmq
spec:
  selector:
    app: rabbitmq
  ports:
    - name: management
      protocol: TCP
      port: 15672
      targetPort: 15672
    - name: rabbit
      protocol: TCP
      port: 5672
      targetPort: 5672
```

```python
# tiltfile - add
k8s_yaml('deploy/rabbitmq.yaml')

k8s_resource(
    'rabbitmq',
    port_forwards=['15672:15672', '5672:5672']
)

```

Watch Tilt Web Console to see the deployment. Afterwards RabbitMQ Manabement Console should be available at http://localhost:15672/. BTW the link is also included in Tilt Web Console.


## Add Producer

### Add dependencies

```bash
poetry add celery
poetry add --group dev celery-types
```

### Producer Task

```python
# dispo/dispo/tasks.py
import logging
import os

from celery import Celery
from celery.signals import worker_process_init

logger = logging.getLogger(__name__)


@worker_process_init.connect(weak=False)
def init_celery_tracing(*args, **kwargs):
    logging.debug("init celery")


amqp_url = os.environ["AMQP_URL"]
app = Celery(broker=amqp_url)

app.conf.task_default_exchange = "dispo"


@app.task(
    name="booking.created", exchange="dispo", routing_key="booking", ignore_result=True
)
def booking_created(data):
    raise NotImplementedError("you must not call me directly! Use delay!")

```

### Add trigger

```python
# dispo/dispo/booking.py - add before return of post method

    logger.info("pushing to queue")
    tasks.booking_created.delay(
        {"room": booking.room.name, "start": booking.start, "end": booking.end}
    )

```


Test it

```bash
curl http://localhost:8080/health

curl http://localhost:8080/api/v1/bookings/  -H "Content-Type: application/json" \
  -d '{"room_id": 1, "start": "2023-02-04", "end": "2023-02-06"}'
```

You may want to update your env vars for local debugging

```json
# dispo/.vscode/launch.json

# beyond this line
      "args": ["dispo.main:app", "--reload"],
# add this
      "env": {
        "DATABASE_URL": "postgresql://dispo:mysecretpassword@localhost/dispo",
        "AMQP_URL": "amqp://rabbit:mysecretpassword@localhost:5672/"
      },
```

Check RabbitMQ Management Console

