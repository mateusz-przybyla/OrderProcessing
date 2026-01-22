from marshmallow import Schema, fields
from marshmallow.validate import Length

from api.schemas.order_item import OrderItemSchema
from api.schemas.order_event import OrderEventSchema

class OrderCreateSchema(Schema):
    error = fields.String(required=False, allow_none=True) # new field to simulate errors
    items = fields.List(
        fields.Nested(OrderItemSchema),
        required=True,
        validate=Length(min=1)
    )

class OrderResponseSchema(Schema):
    uuid = fields.String(dump_only=True)
    status = fields.String(attribute="status_value", dump_only=True)
    total_amount = fields.Decimal(as_string=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class OrderStatusResponseSchema(OrderResponseSchema):
    items = fields.List(fields.Nested(OrderItemSchema), dump_only=True)
    events = fields.List(fields.Nested(OrderEventSchema), dump_only=True)