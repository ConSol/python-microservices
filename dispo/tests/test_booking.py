from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, StaticPool, create_engine

from dispo.database import get_db
from dispo.main import app
from dispo.models import Room


@pytest.fixture(name="db")
def db_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db:
        yield db


@pytest.fixture(name="client")
def client_fixture(db: Session):
    def get_db_override():
        return db

    def booking_created_override():
        return MagicMock()

    app.dependency_overrides[get_db] = get_db_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_booking(db: Session, client: TestClient):
    room = Room(number="666", name="DChamber")
    db.add(room)
    db.commit()

    res = client.post(
        "/api/v1/bookings/",
        json={"room_id": room.id, "start": "2023-04-13", "end": "2023-04-16"},
    )
    data = res.json()

    assert res.status_code == 200
    assert data["room_id"] == room.id
    assert data["start"] == "2023-04-13"
    assert data["end"] == "2023-04-16"
    assert data["id"] is not None
