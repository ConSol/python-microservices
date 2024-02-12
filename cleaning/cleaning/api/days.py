from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlmodel import Session

from cleaning.database import get_db
from cleaning.models import Days

router = APIRouter(prefix="/api/v1/days", tags=["rooms"])


@router.get("/", response_model=List[Days])
def read_all_rooms(
    *,
    db: Session = Depends(get_db),
    start: date = date.today(),
    end: date = date.today() + timedelta(days=7),
):
    days = db.exec(
        text(
            f"""
    SELECT distinct d.day, b.room, case when b.end = d.day then 1 else 0 end as final
    FROM
    (select generate_series(timestamp '{start}', '{end}', '1 day')::date as day) d
    join booking b on b.start <= d.day and b.end >= d.day
    order by 1
"""
        )
    ).all()  # type: ignore
    return days
