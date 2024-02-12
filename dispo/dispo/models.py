from datetime import date
from typing import List, Optional

from pydantic import model_validator
from sqlmodel import Field, Relationship, SQLModel


class RoomBase(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    number: str = Field(index=True)
    name: str


class Room(RoomBase, table=True):
    bookings: List["Booking"] = Relationship(back_populates="room")


class BookingBase(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: Optional[int] = Field(default=None, foreign_key="room.id")
    start: date
    end: date

    @model_validator(mode="after")
    def check_dates(self):
        if self.start >= self.end:
            raise ValueError("start is not before end.")
        return self


class Booking(BookingBase, table=True):
    room: Room = Relationship(back_populates="bookings")


# separate class is needed to allow response including relations
class BookingWithRoom(BookingBase):
    room: Optional[Room] = None
