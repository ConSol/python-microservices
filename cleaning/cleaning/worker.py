import logging
import os

from celery import Celery
from celery.signals import worker_process_init
from kombu import Exchange, Queue
from sqlmodel import Session

from cleaning.database import get_engine
from cleaning.models import Booking

logger = logging.getLogger(__name__)


@worker_process_init.connect(weak=False)
def init_celery_tracing(*args, **kwargs):
    logger.info("CeleryInstrumentator initializing")


amqp_url = os.getenv("AMQP_URL")
app = Celery("worker", broker=amqp_url)

app.conf.task_queues = (Queue("cleaning", Exchange("dispo"), routing_key="booking"),)
app.conf.task_routes = {"cleaning.celery_worker.*": "dispo"}


@app.task(name="booking.created")
def booking_created(data):
    logger.info(f"got message {data}")
    with Session(get_engine()) as db:
        booking = Booking(**data)
        db.add(booking)
        db.commit()
