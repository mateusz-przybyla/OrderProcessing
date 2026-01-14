from marshmallow import Schema, fields, validate

class OrderItemSchema(Schema):
    product_name = fields.String(required=True, validate=validate.Length(min=1))
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    unit_price = fields.Decimal(required=True, as_string=True, validate=validate.Range(min=0.01))