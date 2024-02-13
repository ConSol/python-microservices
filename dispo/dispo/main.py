import logging

from fastapi import Depends, FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator as PrometheusInstrumentator
from sqlalchemy import text
from sqlmodel import Session

from dispo import tasks
from dispo.api import booking, room
from dispo.database import get_db

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(room.router)
app.include_router(booking.router)

prom_instrumentator = PrometheusInstrumentator().instrument(app)
prom_instrumentator.expose(app)


@app.get("/")
async def hello_world():
    logger.debug("here we go")
    return {"message": "hello world"}


@app.get("/health")
def health(
    *,
    db: Session = Depends(get_db),
):
    try:
        # Database
        sql = text("select 1")
        db.exec(sql)  # type: ignore
        # Celery
        tasks.app.control.inspect().active()

    except Exception as ex:
        raise HTTPException(status_code=500, detail=repr(ex))
    return {"message": "OK"}
