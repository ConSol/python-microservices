### Lession 3

# REST Service

## Model

Adding library `poetry add sqlmodel`. SqlModel is SqlAlchemie with an extra portion of Pydantic, used by FastApi.

```python
# dispo/dispo/models.py
from typing import Optional

from sqlmodel import Field, SQLModel


class Room(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    number: str = Field(index=True)
    name: str

```

## Database Connection

```python
# dispo/dispo/database.py
import logging
import os
from functools import cache

from sqlalchemy import create_engine

logger = logging.getLogger(__name__)


@cache
def get_engine():
    database_url = os.environ["DATABASE_URL"]
    engine = create_engine(database_url)
    logger.info(f"using database {engine.url}")
    return engine

```

## Router

```python
# dispo/dispo/api/room.py
import logging
from typing import List

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from dispo.database import get_engine
from dispo.models import Room

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/rooms", tags=["rooms"])


@router.post("/", response_model=Room)
async def create_room(room: Room):
    with Session(get_engine()) as db:
        db.add(room)
        db.commit()
        db.refresh(room)
    return room


@router.get("/", response_model=List[Room])
async def read_all_rooms():
    with Session(get_engine()) as db:
        rooms = db.exec(select(Room)).all()
    return rooms


@router.get("/{room_id}", response_model=Room)
async def read_room(room_id: int):
    with Session(get_engine()) as db:
        room = db.get(Room, room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found.")
    return room

# ... patch, delete
```

Add Router to app
```python
# dispo/dispo/main.py
from dispo.models import Room
# ...
app.include_router(room.router)
```

## Database - Postgres

Create an own image including setup of users and databases.

Add dependency `poetry add psycopg2-binary`

```Dockerfile
# mypostgres/Dockerfile
FROM postgres

COPY ./*.sql /docker-entrypoint-initdb.d/
```

```sql
-- # mypostgres/create_users.sql
CREATE USER dispo PASSWORD 'mysecretpassword';
CREATE DATABASE dispo;
GRANT ALL PRIVILEGES ON DATABASE dispo TO dispo;
GRANT CREATE ON DATABASE dispo to dispo;
ALTER DATABASE dispo OWNER TO dispo;

CREATE USER cleaning PASSWORD 'mysecretpassword';
CREATE DATABASE cleaning;
GRANT ALL PRIVILEGES ON DATABASE cleaning TO cleaning;
GRANT CREATE ON DATABASE cleaning to cleaning;
ALTER DATABASE cleaning OWNER TO cleaning;
```

```yaml
# deploy/postgres.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  labels:
    app: postgres
spec:
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: mypostgres
          ports:
            - containerPort: 5432
          env:
           - name: POSTGRES_PASSWORD
             value: mysecretpassword
           - name: PGDATA
             value: /var/lib/postgresql/data/test
          volumeMounts:
          - name: postgresql-data
            mountPath: /var/lib/postgresql/data
            claimName: postgresql-data
          resources:
            limits:
              memory: 256Mi
              cpu: 400m
      volumes:
      - name: postgresql-data
        persistentVolumeClaim:
          claimName: postgresql-data
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  selector:
    app: postgres
  ports:
    - protocol: TCP
      port: 5432
      targetPort: 5432
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgresql-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 2Gi
```

```python
# tiltfile - add

docker_build(
    'mypostgres',
    context='./mypostgres',
    dockerfile='./mypostgres/Dockerfile',
)

k8s_yaml('deploy/postgres.yaml')

k8s_resource(
    'postgres',
    port_forwards=['5432:5432']
)

```

## Create Schema

```python
# dispo/dispo/database.py - add

def create_schema():
    import dispo.models  # noqa

    SQLModel.metadata.create_all(get_engine())

if __name__ == "__main__":
    # could be explicitly called with
    # kubectl exec deploy/dispo -- python -m dispo.database
    create_schema()
```

To call `create_schema` on startup add following before exec statement in `start*.sh` \
`python -m dispo.database`


## Health Check

```python
# dispo/dispo/main.py - add

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlmodel import Session
from dispo.database import get_db


@app.get("/health")
def health(
    *,
    db: Session = Depends(get_db),
):
    try:
        # Database
        sql = text("select 1")
        db.exec(sql)  # type: ignore

    except Exception as ex:
        raise HTTPException(status_code=500, detail=repr(ex))
    return {"message": "OK"}

```

## Testing Endpoints

OpenAPI http://localhost:8080/docs

```bash
# HEALTH
curl http://localhost:8080/health/

# GET
curl http://localhost:8080/api/v1/rooms/

# POST
curl http://localhost:8080/api/v1/rooms/  -H "Content-Type: application/json" \
  -d '{"number": "123", "name": "President Suite"}'

```

Hint: Dont forget to trailing backslash. The server will respond with 307, but you might not see this when not showing the headers. This depends on how you defined the route. `curl -v http://localhost:8080/api/v1/rooms`

