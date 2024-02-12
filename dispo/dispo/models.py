from datetime import date
from typing import Optional

from pydantic import model_validator
from sqlmodel import Field, SQLModel


class Room(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    number: str = Field(index=True)
    name: str


class Booking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: Optional[int] = Field(default=None, foreign_key="room.id")
    start: date
    end: date

    @model_validator(mode="after")
    def check_dates(self):
        if self.start >= self.end:
            raise ValueError("start is not before end.")
        return self
