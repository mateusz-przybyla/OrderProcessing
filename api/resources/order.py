import uuid
from decimal import Decimal
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint
from flask import current_app
from redis.exceptions import RedisError

from api.extensions import db
from api.models import (
    OrderModel,
    OrderStatus,
    OrderItemModel,
    OrderEventModel,
    OrderEventType
)
from api.schemas import (
    OrderCreateSchema, 
    OrderResponseSchema
)
from api.tasks import order as order_tasks

blp = Blueprint("orders", __name__, description="Order processing endpoints")

@blp.route("/api/orders")
class OrdersResource(MethodView):
    @jwt_required()
    @blp.arguments(OrderCreateSchema)
    @blp.response(201, OrderResponseSchema)
    def post(self, data):
        """Create new order and enqueue async processing task."""

        user_id = get_jwt_identity()

        total_amount = sum(
            Decimal(item['quantity']) * Decimal(item['unit_price'])
            for item in data['items']
        )
        total_amount = total_amount.quantize(Decimal("0.01"))

        order = OrderModel(
            uuid=str(uuid.uuid4()),
            user_id=user_id,
            total_amount=total_amount,
            status=OrderStatus.PENDING
        )
        db.session.add(order)
        db.session.flush()

        for item in data['items']:
            db.session.add(
                OrderItemModel(
                    order_id=order.id,
                    product_name=item['product_name'],
                    quantity=item['quantity'],
                    unit_price=item['unit_price']
                )
            )
        db.session.add(
            OrderEventModel(
                order_id=order.id,
                event_type=OrderEventType.ORDER_CREATED
            )
        )
        db.session.add(
            OrderEventModel(
                order_id=order.id,
                event_type=OrderEventType.ORDER_ENQUEUED,
            )
        )
        db.session.commit()

        try:
            order_tasks.process_order_task.delay(order.id, data.get('error'))
        except RedisError as e:
            current_app.logger.error(
                "Failed to enqueue async task for order processing.",
                extra={"error": str(e), "order_id": order.id}
            )

        return order