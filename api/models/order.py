import enum

from api.extensions import db

class OrderStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class OrderModel(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    status = db.Column(
        db.Enum(OrderStatus),
        default=OrderStatus.PENDING,
        nullable=False,
        index=True
    )
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

    # Relationships
    user = db.relationship("UserModel", back_populates="orders")
    items = db.relationship(
        "OrderItemModel", 
        back_populates="order", 
        cascade="all, delete-orphan"
    )
    events = db.relationship(
        "OrderEventModel",
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="OrderEventModel.created_at"
    )

    def __repr__(self):
        return f"<Order id={self.id} status={self.status.value}>"
    
    @property
    def status_value(self):
        return self.status.value