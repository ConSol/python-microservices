import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from dispo import tasks
from dispo.database import get_db
from dispo.models import Booking, BookingBase, BookingWithRoom

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/bookings", tags=["bookings"])

SessionDep = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=Booking)
def create_booking(
    booking_data: BookingBase,
    db: SessionDep,
):
    booking = Booking.model_validate(booking_data)
    db.add(booking)
    db.commit()
    db.refresh(booking)

    logger.info("pushing to queue")
    tasks.booking_created.delay(
        {"room": booking.room.name, "start": booking.start, "end": booking.end}
    )

    return booking


@router.get("/", response_model=List[Booking])
async def read_all_bookings(db: SessionDep):
    bookings = db.exec(select(Booking)).all()
    return bookings


@router.get("/{booking_id}", response_model=BookingWithRoom)
async def read_booking(booking_id: int, db: SessionDep):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    return booking


@router.patch("/{booking_id}", response_model=Booking)
async def update_booking(booking_id: int, booking: Booking, db: SessionDep):
    db_booking = db.get(Booking, booking_id)
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    booking_data = booking.model_dump(exclude_unset=True)
    for key, value in booking_data.items():
        setattr(db_booking, key, value)
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


@router.delete("/{booking_id}")
async def delete_booking(booking_id: int, db: SessionDep):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    db.delete(booking)
    db.commit()
