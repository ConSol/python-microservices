import logging
import os

from celery import Celery
from celery.signals import worker_process_init

logger = logging.getLogger(__name__)


@worker_process_init.connect(weak=False)
def init_celery_tracing(*args, **kwargs):
    logging.debug("init celery")


amqp_url = os.environ["AMQP_URL"]
app = Celery(broker=amqp_url)

app.conf.task_default_exchange = "dispo"


@app.task(
    name="booking.created", exchange="dispo", routing_key="booking", ignore_result=True
)
def booking_created(data):
    raise NotImplementedError("you must not call me directly! Use delay!")
