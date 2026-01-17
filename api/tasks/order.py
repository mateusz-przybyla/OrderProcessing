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

@celery.task(
    bind=True,
    autoretry_for=(TemporaryInfrastructureError,),
    retry_backoff=True,
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
        order.status = OrderStatus.FAILED
        db.session.add(
            OrderEventModel(
                order_id=order.id,
                event_type=OrderEventType.PROCESSING_FAILED,
                payload={"reason": str(e)}
            )
        )
        db.session.commit()
        return
    except TemporaryInfrastructureError:
        raise

    order.status = OrderStatus.COMPLETED
    db.session.add(
        OrderEventModel(
            order_id=order.id,
            event_type=OrderEventType.ORDER_COMPLETED
        )
    )
    db.session.commit()

def process_order_business_logic(error: str | None) -> None:
    # Simulate order processing logic
    time.sleep(5)

    if error == "business":
        raise BusinessLogicError("Simulated business logic error.")
    elif error == "infrastructure":
        raise TemporaryInfrastructureError("Simulated temporary infrastructure error.")