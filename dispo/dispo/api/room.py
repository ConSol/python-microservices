import logging
from datetime import date
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, and_, not_, select

from dispo.database import get_db
from dispo.models import Booking, Room

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/rooms", tags=["rooms"])

SessionDep = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=Room)
async def create_room(room: Room, db: SessionDep):
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.get("/", response_model=List[Room])
async def read_all_rooms(db: SessionDep):
    rooms = db.exec(select(Room)).all()
    return rooms


@router.get("/{room_id}", response_model=Room)
async def read_room(room_id: int, db: SessionDep):
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")
    return room


@router.patch("/{room_id}", response_model=Room)
async def update_room(room_id: int, room: Room, db: SessionDep):
    db_room = db.get(Room, room_id)
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found.")
    hero_data = room.model_dump(exclude_unset=True)
    for key, value in hero_data.items():
        setattr(db_room, key, value)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


@router.delete("/{room_id}")
async def delete_room(room_id: int, db: SessionDep):
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")
    db.delete(room)
    db.commit()


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
