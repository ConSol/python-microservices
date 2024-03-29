from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, StaticPool, create_engine

from dispo.database import get_db
from dispo.main import app
from dispo.models import Booking, Room


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


def test_patch_room(session: Session, client: TestClient):
    room = Room(number="345", name="Wedding Suite")
    session.add(room)
    session.commit()

    res = client.patch(f"/api/v1/rooms/{room.id}", json={"name": "Honeymoon Suite"})
    data = res.json()

    assert res.status_code == 200
    assert data["number"] == "345"
    assert data["name"] == "Honeymoon Suite"
    assert data["id"] == room.id


@pytest.mark.parametrize(
    "start, end, expected",
    [
        ("2024-04-02", "2024-04-04", True),
        ("2024-04-01", "2024-04-06", False),
        ("2024-04-02", "2024-04-06", False),
        ("2024-04-01", "2024-04-04", False),
    ],
)
def test_room_free(start, end, expected, session: Session, client: TestClient):
    room1 = Room(number="123", name="President Suite")
    room2 = Room(number="345", name="Wedding Suite")
    session.add(room1)
    session.add(room2)
    booking1 = Booking(room_id=room1.id, start=date(2024, 4, 4), end=date(2024, 4, 6))
    booking2 = Booking(room_id=room1.id, start=date(2024, 4, 1), end=date(2024, 4, 2))
    session.add(booking1)
    session.add(booking2)
    session.commit()

    res = client.get(f"/api/v1/rooms/free/?start={start}&end={end}")
    data: list = res.json()

    assert res.status_code == 200
    included = len([room for room in data if room["id"] == room1.id]) == 1
    assert included == expected
