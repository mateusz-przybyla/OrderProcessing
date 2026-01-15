import enum

from api.extensions import db

class OrderEventType(enum.Enum):
    ORDER_CREATED = "order_created"
    ORDER_ENQUEUED = "order_enqueued"
    PROCESSING_STARTED = "processing_started"
    PROCESSING_FAILED = "processing_failed"
    ORDER_COMPLETED = "order_completed"
    ORDER_CANCELLED = "order_cancelled"

class OrderEventModel(db.Model):
    __tablename__ = "order_events"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)

    event_type = db.Column(
        db.Enum(OrderEventType, name="order_event_type_enum"),
        nullable=False,
        index=True
    )
    payload = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    # Relationships
    order = db.relationship("OrderModel", back_populates="events")

    def __repr__(self):
        return f"<OrderEvent order_id={self.order_id} event={self.event_type.value}>"