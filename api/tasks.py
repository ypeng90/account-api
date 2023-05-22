from celery import shared_task
from datetime import datetime, timedelta
from .utils import Gmail


@shared_task(
    # Bind to self instance for a reference to the task object.
    # bind=True,
    # In-queue expiry time: in 1 hour
    utc=True,
    expires=datetime.utcnow() + timedelta(hours=1),
    # Execution time limits (soft, hard)
    # SoftTimeLimitExceeded exception is raised when soft time limit is reached.
    timelimit=(25, 30),
    # Acknowledge after execution for idempotent procedures.
    acks_late=True,
    # Retry with max_retries and backoff.
    autoretry_for=(Exception,),
    max_retries=5,
    retry_backoff=True,
    # Select queue.
    queue="slow",
)
def send_gmail(message):
    # Must add self when bind=True is used, otherwise must remove self.
    client = Gmail()
    client.send_message(message)
    # Close httplib2 connections, not the service object.
    client.service.close()
