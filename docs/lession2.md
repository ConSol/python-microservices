### Lession 2

# Up into Kubernetes

## Python Package

For a better file structure of our app move the main.py to subdir `dispo`.
```sh
mkdir dispo/dispo
mv dispo/main.py dispo/dispo/main.py

```

The whole project should look like this:

```sh
# tree
├── dispo
│   ├── Dockerfile
│   ├── README.md
│   ├── __pycache__
│   │   └── main.cpython-312.pyc
│   ├── dispo
│   │   ├── __pycache__
│   │   │   └── main.cpython-312.pyc
│   │   └── main.py
│   ├── log_conf.yaml
│   ├── poetry.lock
│   ├── pyproject.toml
│   └── start.sh
└── docs
    ├── lession1.md
    └── lession2.md
```

Change start param of uvicorn in launch.json and start.sh to `dispo.main:app`

## Dockerize

Create Dockerfile which will install dependencies and copy the project into it. Use shell script to start uvicorn.

Use multistage dockerfile to avoid having poetry in production image.

```docker
# dispo/Dockerfile
FROM python:3.12 as base

WORKDIR /svc

RUN pip install poetry && \
  python -m venv /venv

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt | \
  /venv/bin/pip install -r /dev/stdin


FROM python:3.12

WORKDIR /svc

COPY --from=base /venv /venv
COPY . .
RUN chmod u+x *.sh

EXPOSE 8000

CMD ["./start.sh"]
```

```sh
# dispo/start.sh
#!/bin/sh

set -e

. /venv/bin/activate

exec uvicorn \
  --host 0.0.0.0 \
  --log-config=log_conf.yaml \
  dispo.main:app
```

Test Dockerfile
```sh
docker build -t dispo  .
docker run -p 8000:8000 dispo
```

## Logging

```yaml
# dispo/log_conf.yaml
version: 1
disable_existing_loggers: False
formatters:
  default:
    # "()": uvicorn.logging.DefaultFormatter
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  access:
    # "()": uvicorn.logging.AccessFormatter
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  default:
    formatter: default
    class: logging.StreamHandler
    stream: ext://sys.stderr
  access:
    formatter: access
    class: logging.StreamHandler
    stream: ext://sys.stdout
loggers:
  uvicorn.error:
    level: INFO
    handlers:
      - default
    propagate: no
  uvicorn.access:
    level: INFO
    handlers:
      - access
    propagate: no
root:
  level: DEBUG
  handlers:
    - default
  propagate: no
```

Add uvicorn param to dispo/start.sh: \
`--log-config=log_conf.yaml`

We need additional library to enable yaml files: \
`poetry add pyyaml`

This is how logging is done in python, add this to our main.py

```python
# add to dispo/dispo/main.py
import logging
logger = logging.getLogger(__name__)

# best to place inside of hello_world()
    logger.debug("here we go")
```

## Tilt & Debug

Move up to Kubernetes

Start up Tilt inside our root folder (not `dispo`) \
`tilt up` and let him create a Tiltfile. Apply the following - you may want to adopt it to the existing structure:

```python
# tiltfile
docker_build(
    'dispo',
    context='./dispo',
    dockerfile='./dispo/Dockerfile',
    entrypoint=["./start-debug.sh"],
    ignore=["**/__pycache__", ".pytest_cache", "**/*.pyc*"],
    live_update=[
        sync('./dispo/dispo', '/svc/dispo'),
    ],
)

k8s_yaml('deploy/dispo.yaml')

k8s_resource(
    'dispo',
    port_forwards=['8080:8000', '5678:5678']
)

```

Here are some missing files:

```sh
# dispo/start-debug.sh
#!/bin/sh

set -e

. /venv/bin/activate

exec python \
  -m debugpy --listen 0.0.0.0:5678 \
  -m uvicorn \
  --host 0.0.0.0 \
  --log-config=log_conf.yaml \
  --reload \
  dispo.main:app
```

```yaml
# deploy/dispo.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dispo
  labels:
    app: dispo
spec:
  selector:
    matchLabels:
      app: dispo
  template:
    metadata:
      labels:
        app: dispo
    spec:
      containers:
        - name: dispo
          image: dispo
          ports:
            - containerPort: 8000
            - containerPort: 5678
          env:
            - name: DATABASE_URL
              value: postgresql://dispo:mysecretpassword@postgres/dispo
            - name: AMQP_URL
              value: amqp://rabbit:mysecretpassword@rabbitmq:5672/
            - name: OTEL_EXPORTER_OTLP_ENDPOINT
              value: http://jaeger:4317
            - name: OTEL_SERVICE_NAME
              value: dispo
          resources:
            limits:
              memory: 256Mi
              cpu: 400m
---
apiVersion: v1
kind: Service
metadata:
  name: dispo
spec:
  selector:
    app: dispo
  ports:
    - name: api
      protocol: TCP
      port: 80
      targetPort: 8000
    - name: debugger
      protocol: TCP
      port: 5678
      targetPort: 5678
```

Add missing dependency, execute inside `/dispo`: \
`poetry add pydebug`

Last you have to add a configuration to `Run & Debug`
Check: Python Debugger - Remote Attach. Default values should do the job.

### Now check:
- Check the Tilt Browser (press space in terminal with tilt process)
- Access service on kubernetes - http://localhost:8080
- Modify file (e.g. logging statement in main.py)
- Set a breakpoint


