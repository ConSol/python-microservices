# Welcome to Tilt!
#   To get you started as quickly as possible, we have created a
#   starter Tiltfile for you.
#
#   Uncomment, modify, and delete any commands as needed for your
#   project's configuration.


# Output diagnostic messages
#   You can print log messages, warnings, and fatal errors, which will
#   appear in the (Tiltfile) resource in the web UI. Tiltfiles support
#   multiline strings and common string operations such as formatting.
#
#   More info: https://docs.tilt.dev/api.html#api.warn
warn('ℹ️ Open {tiltfile_path} in your favorite editor to get started.'.format(
    tiltfile_path=config.main_path))


# Build Docker image
#   Tilt will automatically associate image builds with the resource(s)
#   that reference them (e.g. via Kubernetes or Docker Compose YAML).
#
#   More info: https://docs.tilt.dev/api.html#api.docker_build
#
# docker_build('registry.example.com/my-image',
#              context='.',
#              # (Optional) Use a custom Dockerfile path
#              dockerfile='./deploy/app.dockerfile',
#              # (Optional) Filter the paths used in the build
#              only=['./app'],
#              # (Recommended) Updating a running container in-place
#              # https://docs.tilt.dev/live_update_reference.html
#              live_update=[
#                 # Sync files from host to container
#                 sync('./app', '/src/'),
#                 # Execute commands inside the container when certain
#                 # paths change
#                 run('/src/codegen.sh', trigger=['./app/api'])
#              ]
# )
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

docker_build(
    'mypostgres',
    context='./mypostgres',
    dockerfile='./mypostgres/Dockerfile',
)

docker_build(
    'cleaning',
    context='./cleaning',
    dockerfile='./cleaning/worker.Dockerfile',
    entrypoint=["./start-debug.sh"],
    ignore=["**/__pycache__", ".pytest_cache", "**/*.pyc*"],
    live_update=[
        sync('./cleaning/cleaning', '/svc/cleaning'),
    ],
)

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

docker_build(
    'myprometheus',
    context='./myprometheus',
    dockerfile='./myprometheus/Dockerfile'
)


# Apply Kubernetes manifests
#   Tilt will build & push any necessary images, re-deploying your
#   resources as they change.
#
#   More info: https://docs.tilt.dev/api.html#api.k8s_yaml
#
# k8s_yaml(['k8s/deployment.yaml', 'k8s/service.yaml'])
k8s_yaml('deploy/dispo.yaml')
k8s_yaml('deploy/postgres.yaml')
k8s_yaml('deploy/rabbitmq.yaml')
k8s_yaml('deploy/cleaning.yaml')
k8s_yaml('deploy/cleaning_worker.yaml')
k8s_yaml('deploy/prometheus.yaml')
k8s_yaml('deploy/jaeger.yaml')

# Customize a Kubernetes resource
#   By default, Kubernetes resource names are automatically assigned
#   based on objects in the YAML manifests, e.g. Deployment name.
#
#   Tilt strives for sane defaults, so calling k8s_resource is
#   optional, and you only need to pass the arguments you want to
#   override.
#
#   More info: https://docs.tilt.dev/api.html#api.k8s_resource
#
# k8s_resource('my-deployment',
#              # map one or more local ports to ports on your Pod
#              port_forwards=['5000:8080'],
#              # change whether the resource is started by default
#              auto_init=False,
#              # control whether the resource automatically updates
#              trigger_mode=TRIGGER_MODE_MANUAL
# )
k8s_resource(
    'dispo',
    port_forwards=['8080:8000', '5678:5678']
)

k8s_resource(
    'postgres',
    port_forwards=['5432:5432']
)

k8s_resource(
    'rabbitmq',
    port_forwards=['15672:15672', '5672:5672']
)

k8s_resource(
    'cleaning',
    port_forwards=['8081:8000', '5679:5678']
)

k8s_resource(
    'cleaning.worker',
    port_forwards=['5680:5678']
)

k8s_resource(
    'prometheus',
    port_forwards=['9090:9090']
)

k8s_resource(
    'jaeger',
    port_forwards=['16686:16686', '4317:4317']
)

# Run local commands
#   Local commands can be helpful for one-time tasks like installing
#   project prerequisites. They can also manage long-lived processes
#   for non-containerized services or dependencies.
#
#   More info: https://docs.tilt.dev/local_resource.html
#
# local_resource('install-helm',
#                cmd='which helm > /dev/null || brew install helm',
#                # `cmd_bat`, when present, is used instead of `cmd` on Windows.
#                cmd_bat=[
#                    'powershell.exe',
#                    '-Noninteractive',
#                    '-Command',
#                    '& {if (!(Get-Command helm -ErrorAction SilentlyContinue)) {scoop install helm}}'
#                ]
# )

