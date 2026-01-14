from marshmallow import Schema, fields
from marshmallow.validate import Length

from api.schemas.order_item import OrderItemSchema

class OrderCreateSchema(Schema):
    items = fields.List(
        fields.Nested(OrderItemSchema),
        required=True,
        validate=Length(min=1)
    )

class OrderResponseSchema(Schema):
    uuid = fields.String(dump_only=True)
    status = fields.Method("get_status", dump_only=True)
    total_amount = fields.Decimal(as_string=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    def get_status(self, obj):
        return obj.status.value