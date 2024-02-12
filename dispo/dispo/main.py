import logging

from fastapi import FastAPI

from dispo.api import booking, room

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(room.router)
app.include_router(booking.router)


@app.get("/")
async def hello_world():
    logger.debug("here we go")
    return {"message": "hello world"}
