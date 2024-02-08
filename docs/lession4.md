### Lession 4

# Unit Testing

## Dependency Injection

As preperation for testing.

```python
# dispo/dispo/api/room.py

# add
SessionDep = Annotated[Session, Depends(get_db)]

# change
async def create_room(room: Room):
    with Session(get_engine()) as db:
        db.add(room)
        db.commit()
        db.refresh(room)
# to
async def create_room(room: Room, db: SessionDep):
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

# same for all other routes

```

```python
# dispo/dispo/database.py
# add
def get_db() -> Generator:
    with Session(get_engine()) as session:
        yield session
```

## Writing Test

Add pytest and httpx as dev dependency.

`poetry add --group dev pytest httpx`

```python
# dispo/test/test_room.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, StaticPool, create_engine

from dispo.database import get_db
from dispo.main import app
from dispo.models import Room


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_db_override():
        return session

    app.dependency_overrides[get_db] = get_db_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_room(client: TestClient):
    res = client.post(
        "/api/v1/rooms", json={"number": "123", "name": "President Suite"}
    )

    data = res.json()

    assert res.status_code == 200
    assert data["number"] == "123"
    assert data["name"] == "President Suite"
    assert data["id"] is not None


```

Config and run test in VS-Code

### Task

- Write test for method patch
- you have to create the room first by sqlmodel
- Story could be: Rename Wedding Suite to Honeymoon Suite


