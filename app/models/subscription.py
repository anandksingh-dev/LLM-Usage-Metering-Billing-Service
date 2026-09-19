from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func

from app.db.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    tenant_id = Column(
        Integer,
        ForeignKey("tenants.id"),
        nullable=False
    )

    plan_id = Column(
        Integer,
        ForeignKey("plans.id"),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False
    )

    stripe_customer_id = Column(
        String(255),
        nullable=True,
        index=True
    )

    stripe_subscription_id = Column(
        String(255),
        nullable=True,
        index=True
    )

    current_period_start = Column(
        DateTime(timezone=True),
        nullable=True
    )

    current_period_end = Column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )