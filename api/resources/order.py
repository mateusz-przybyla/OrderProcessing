import uuid
from decimal import Decimal
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint

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

blp = Blueprint("orders", __name__, description="Order processing endpoints")

@blp.route("/api/orders")
class OrdersResource(MethodView):
    @jwt_required()
    @blp.arguments(OrderCreateSchema)
    @blp.response(201, OrderResponseSchema)
    def post(self, data):
        """
        Create new order
        """
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

        db.session.commit()

        return order