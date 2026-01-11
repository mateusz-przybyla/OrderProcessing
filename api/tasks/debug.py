import time
from flask import current_app

from api.celery_app import celery

@celery.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=5,
    retry_kwargs={"max_retries": 3}
)
def long_running_task(self, seconds):
    time.sleep(seconds)
    return f"Task completed after {seconds} seconds."

@celery.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=3,
    retry_kwargs={"max_retries": 3}
)
def test_retry_task(self, should_fail: bool) -> str:
    current_app.logger.info(f"Task {self.request.id} started, should_fail={should_fail}")

    if should_fail and self.request.retries < 2:
        raise Exception("Intentional failure for testing retries")

    current_app.logger.info("Task completed successfully.")
    
    return "OK"