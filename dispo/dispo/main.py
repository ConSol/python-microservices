import logging

from fastapi import FastAPI

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def hello_world():
    logger.debug("here we go")
    return {"message": "hello world"}
