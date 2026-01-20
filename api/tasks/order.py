import time

from api.extensions import db
from api.celery_app import celery
from api.models import (
    OrderModel, 
    OrderEventModel, 
    OrderStatus, 
    OrderEventType
)
from api.exceptions import BusinessLogicError, TemporaryInfrastructureError

def _mark_order_failed(
    order: OrderModel,
    *,
    reason: str,
    error: str,
    retries: int | None = None,
) -> None:
    order.status = OrderStatus.FAILED

    payload = {
        "reason": reason,
        "error": error
    }
    if retries is not None:
        payload['retries'] = retries

    db.session.add(
        OrderEventModel(
            order_id=order.id,
            event_type=OrderEventType.PROCESSING_FAILED,
            payload=payload,
        )
    )
    db.session.commit()

@celery.task(
    bind=True,
    retry_kwargs={"max_retries": 3}
)
def process_order_task(self, order_id: int, error: str | None) -> None:
    order = OrderModel.query.filter_by(id=order_id).first()
    if not order:
        return

    if order.status != OrderStatus.PROCESSING:
        order.status = OrderStatus.PROCESSING
        db.session.add(
            OrderEventModel(
                order_id=order.id,
                event_type=OrderEventType.PROCESSING_STARTED
            )
        )
        db.session.commit()

    try:
        process_order_business_logic(error)
    except BusinessLogicError as e:
        _mark_order_failed(
            order,
            reason="business",
            error=str(e)
        )
        return
    except TemporaryInfrastructureError as e:
        if self.request.retries >= self.max_retries:
            _mark_order_failed(
                    order,
                    reason="infrastructure",
                    error=str(e),
                    retries=self.request.retries
                )
            raise

        countdown = 30 * (2 ** self.request.retries)
        raise self.retry(exc=e, countdown=countdown)

    order.status = OrderStatus.COMPLETED
    db.session.add(
        OrderEventModel(
            order_id=order.id,
            event_type=OrderEventType.ORDER_COMPLETED
        )
    )
    db.session.commit()

def process_order_business_logic(error: str | None) -> None:
    """
    Simulate order processing business logic.
    This function can raise exceptions to simulate different failure scenarios.
    1. BusinessLogicError: Simulates a business logic failure (e.g., validation error).
    2. TemporaryInfrastructureError: Simulates a temporary infrastructure failure (e.g., network issue).
    """
    time.sleep(5)

    if error == "business":
        raise BusinessLogicError("Simulated business logic error.")
    elif error == "infrastructure":
        raise TemporaryInfrastructureError("Simulated temporary infrastructure error.")