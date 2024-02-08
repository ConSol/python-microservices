### Lession 6

# Model Details

## Nested Models

When accessing bookings we only get the primary key of the room, not the entity itself. This is intended behaviour of sqlmodel. Because of the exising backreference the room do also have a list of bookings. Resolving nested references would lead to huge data dumps and to infinite loop (room-bookings-room-...).

To display nested models we have to define a separate model. Inheritence helps us to reduce repeating definitions.

```python
# dispo/dispo/models.py - changes
class BookingBase(SQLModel): # <- base class with NO table attribute
    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: Optional[int] = Field(default=None, foreign_key="room.id")
    start: date
    end: date


class Booking(BookingBase, table=True): # <- class WITH table attribute
    room: Room = Relationship(back_populates="bookings") # <- reference definition with backreference


# separate class is needed to allow response including relations
class BookingWithRoom(BookingBase):
    room: Optional[Room] = None # <- resolved reference entity

```

Now we can change the the response and data type:

```python
# dispo/dispo/api/booking.py

@router.get("/{booking_id}", response_model=BookingWithRoom)
def create_booking(
    booking_data: BookingBase,   # <- important, do NOT use Booking here
    db: SessionDep,
):
  #...

```

Data type must be BookingBase, otherwise sqlalchemy expect the room to be set as an entity!


## Separate Model for Creation

When create a new entity the id-field must be empty. The model definition does not represent this for sake of simplicity. You may want to distinct between `base` and `create` model classes.


## Working with Entities

Add an endpoint to show up all rooms without a booking in a given date range.

```python
# dispo/dispo/api/room.py - add

@router.get("/free/")
async def rooms_free(start: date, end: date, db: SessionDep):
    query = select(Booking.room_id).where(
        and_(Booking.start < end, Booking.end > start)
    )
    room_ids = db.exec(query).all()
    logger.info(f"{start} - {end} : {room_ids}")
    filter_clause = not_(Room.id.in_(room_ids))
    rooms = db.exec(select(Room).filter(filter_clause)).all()
    return rooms

```

So this is way more logic then we had before. Thus we have to test it.

```python
# dispo/test/test_booking.py - add
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

```

