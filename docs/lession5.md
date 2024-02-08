### Lession 5

# Relations on Entities

Combine Rooms with Bookings

```python
# dispo/dispo/models.py - add

class Booking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: Optional[int] = Field(default=None, foreign_key="room.id")
    start: date
    end: date

```


## Functional Validators

Could be added to model. Validation is done for all REST Methods on incomming data. It is based uppon pydantic, the underlying library of sqlmodel.

https://docs.pydantic.dev/latest/api/functional_validators/


```python
# dispo/dispo/models.py - add next to Booking
    @model_validator(mode="after")
    def check_dates(self):
        if self.start >= self.end:
            raise ValueError("start is not before end.")
        return self

```

## Booking API

Create API for Bookings analoque to Rooms.

- CRUD into dispo/dispo/api/booking.py
- add router to dispo/dispo/main.py
- add test for create booking dispo/test/test_booking.py

## Testing Endpoints

```bash
# GET
curl http://localhost:8000/api/v1/bookings/

# POST
curl http://localhost:8000/api/v1/bookings/  -H "Content-Type: application/json" \
  -d '{"room_id": 1, "start": "2023-02-04", "end": "2023-02-06"}'

```

