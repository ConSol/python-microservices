from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from sqlmodel import Session, text

from cleaning import database
from cleaning.api import days
from cleaning.database import get_db
from cleaning.tracing import setup_tracing


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    # just lazy, should be called explicitly
    database.create_schema()

    yield

    # shutdown
    pass


app = FastAPI(lifespan=lifespan)
app.include_router(days.router)

setup_tracing()
FastAPIInstrumentor().instrument_app(app)


@app.get("/health")
def health(*, db: Session = Depends(get_db)):
    try:
        # Database
        # Database
        sql = text("select 1")
        db.exec(sql)  # type: ignore

    except Exception as ex:
        raise HTTPException(status_code=500, detail=repr(ex))
    return {"message": "OK"}
