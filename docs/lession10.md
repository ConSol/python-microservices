### Lession 10

# Monitoring

This is optional step as Prometheus is also included in OpenTelementry, which we will do next.

In this example we will only instrument FastApi. There is also an instrumention solution for Celery.

## Add dependencies

```bash
poetry add prometheus_fastapi_instrumentator

```


## Add Instrumentation

```python
# dispo/dispo/main.py - add
from prometheus_fastapi_instrumentator import Instrumentator as PrometheusInstrumentator

# add beyond app creation
prom_instrumentator = PrometheusInstrumentator().instrument(app)
prom_instrumentator.expose(app)

```

## Add Collector


```docker
# prometheus/Dockerfile
FROM prom/prometheus
ADD prometheus.yml /etc/prometheus/

```

```yaml
global:
  scrape_interval: "15s"
scrape_configs:
  - job_name: 'dispo'
    static_configs:
    - targets: ['dispo:80']

```

```yaml
# deploy/prometheus.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  labels:
    app: prometheus
spec:
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
        - name: prometheus
          image: myprometheus
          ports:
            - containerPort: 9090
          resources:
            limits:
              memory: 256Mi
              cpu: 400m
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
spec:
  selector:
    app: prometheus
  ports:
    - protocol: TCP
      port: 9090
      targetPort: 9090
```

```python
# Tiltfile - add
docker_build(
    'myprometheus',
    context='./myprometheus',
    dockerfile='./myprometheus/Dockerfile'
)

k8s_yaml('deploy/prometheus.yaml')

k8s_resource(
    'prometheus',
    port_forwards=['9090:9090']
)

```



## Testing

```bash
curl http://localhost:8080/metrics

```

Prometheus: http://localhost:9090
