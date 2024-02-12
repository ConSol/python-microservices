from datetime import date
from typing import Optional
from sqlmodel import Field, SQLModel


class Booking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    room: str
    start: date
    end: date


class Days(SQLModel):
    day: date
    room: Optional[str]
    final: int
