import time
import random

from api.extensions import db
from api.celery_app import celery
from api.models import (
    OrderModel, 
    OrderEventModel, 
    OrderStatus, 
    OrderEventType
)

@celery.task(bind=True)
def process_order_task(self, order_id: int) -> None:
    order = OrderModel.query.filter_by(id=order_id).first()
    if not order:
        return

    order.status = OrderStatus.PROCESSING
    db.session.add(
        OrderEventModel(
            order_id=order.id,
            event_type=OrderEventType.PROCESSING_STARTED
        )
    )

    # Simulate order processing
    time.sleep(10)
    
    if random.choice([True, False]):
        order.status = OrderStatus.FAILED
        db.session.add(
            OrderEventModel(
                order_id=order.id,
                event_type=OrderEventType.PROCESSING_FAILED,
                payload={"reason": "Random processing failure"},
            )
        )
        db.session.commit()
        return

    order.status = OrderStatus.COMPLETED
    db.session.add(
        OrderEventModel(
            order_id=order.id,
            event_type=OrderEventType.ORDER_COMPLETED
        )
    )
    db.session.commit()