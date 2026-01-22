from marshmallow import Schema, fields

class OrderEventSchema(Schema):
    event_type = fields.Str(attribute="event_type_name")
    created_at = fields.DateTime()
    payload = fields.Dict()