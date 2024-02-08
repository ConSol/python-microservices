### Lession 11

# Tracing

## Dependencies

For both microservices

```python
poetry add opentelemetry-distro \
  opentelemetry-exporter-otlp-proto-grpc \
  opentelemetry-instrumentation-fastapi \
  opentelemetry-instrumentation-celery \
  opentelemetry-instrumentation-sqlalchemy \
  opentelemetry-instrumentation-logging

```

## Helper

```python
# dispo/dispo/tracing.py & cleaning/cleaning/tracing.py
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# enable console exporter for traces
debug = False


def setup_tracing():
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    tracer_provider = TracerProvider()
    if endpoint is not None:
        tracer_provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(
                    endpoint=os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"],
                )
            )
        )

    if debug:
        tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(tracer_provider)
```

## Instrumentations

FastAPI

```python
# dispo/dispo/main.py & cleaning/cleaning/main.py - add
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from dispo.tracing import setup_tracing

# add above logger creation
setup_tracing()
# add beyond creation of app
FastAPIInstrumentor().instrument(app)
```

Database

```python
# dispo/dispo/database.py & cleaning/cleaning/databae.py - add
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# inside of get_engine
    SQLAlchemyInstrumentor().instrument(engine=engine)
```

Celery - Worker

```python
# cleaning/cleaning/worker.py - add
from opentelemetry.instrumentation.celery import CeleryInstrumentor

@worker_process_init.connect(weak=False)
def init_celery_tracing(*args, **kwargs):
    logger.info("CeleryInstrumentator initializing")
    setup_tracing()
    CeleryInstrumentor().instrument()
```

Celery - Tasks

```python
# dispo/dispo/tasks.py - add
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from dispo.tracing import setup_tracing

@worker_process_init.connect(weak=False)
def init_celery_tracing(*args, **kwargs):
    logger.info("CeleryInstrumentator initializing")
    setup_tracing()
    CeleryInstrumentor().instrument()
```

## Collector

For demo purposes we using a very simple all-in-one package from Jaeger

```yaml
# deploy/jaeger.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
  labels:
    app: jaeger
spec:
  selector:
    matchLabels:
      app: jaeger
  template:
    metadata:
      labels:
        app: jaeger
    spec:
      containers:
        - name: jaeger
          image: jaegertracing/all-in-one
          ports:
            - containerPort: 6831
              protocol: UDP
            - containerPort: 6832
              protocol: UDP
            - containerPort: 5775
              protocol: UDP
            - containerPort: 6831
              protocol: UDP
            - containerPort: 6832
              protocol: UDP
            - containerPort: 5778
            - containerPort: 16686
            - containerPort: 14250
            - containerPort: 14268
            - containerPort: 14269
            - containerPort: 4317
            - containerPort: 4318
            - containerPort: 9411
          env:
            - name: COLLECTOR_OTLP_ENABLED
              value: "true"
          resources:
            limits:
              memory: 512Mi
              cpu: 400m
---
apiVersion: v1
kind: Service
metadata:
  name: jaeger
spec:
  selector:
    app: jaeger
  ports:
    - name: otlp-grpc
      port: 4317
      targetPort: 4317
    - name: otlp
      port: 4318
      targetPort: 4318
```

### Tiltfile

```python
# tiltfile - add
k8s_yaml('deploy/jaeger.yaml')


k8s_resource(
    'jaeger',
    port_forwards=['16686:16686', '4317:4317']
)


```

## Testing

Open Jaeger UI - http://localhost:16686/search

```bash
curl http://localhost:8080/api/v1/bookings/  -H "Content-Type: application/json" \
  -d '{"room_id": 1, "start": "2023-02-04", "end": "2023-02-06"}'
```

Hint: Do not use reload of the whole Jaeger UI! - The timestamp for searching will kept the same and you will never get any changes displayed. Use the search button.

Hint: If your service does not send traces to jaegger, you should first try to restart the pod. With just replacing the code you might miss the re-instanciation of the app.


## Add further Informations

### Spans

```python
from opentelemetry import trace

# near logger
tracer = trace.get_tracer(__name__)


# wrap around your code as new block
        with tracer.start_as_current_span("foo"):
            # ...your code here ...

# or use decorator

    @tracer.start_as_current_span("gah")
    def your_function():
        # ...
```

### Attributes

Attributes are kept as tags for a specific span. You will find these as tags inside the span of Jaeger UI.

```python
  trace.get_current_span().set_attribute("room", booking.room)
```

### Events

Events are most likely Log messages, intended to identify events. You will find these events as logs ;-) inside the span of Jaeger UI.

```python
    trace.get_current_span().add_event(
        "message.received", attributes={"payload": booking.model_dump_json()}
    )
```