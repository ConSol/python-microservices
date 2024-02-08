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


@router.patch("/{room_id}", response_model=Room)
async def update_room(room_id: int, room: Room):
    with Session(get_engine()) as db:
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
async def delete_room(room_id: int):
    with Session(get_engine()) as db:
        room = db.get(Room, room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found.")
        db.delete(room)
        db.commit()
