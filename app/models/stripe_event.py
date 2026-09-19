from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from app.db.database import Base


class StripeEvent(Base):
    __tablename__ = "stripe_events"

    id = Column(Integer, primary_key=True, index=True)

    event_id = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    event_type = Column(
        String(100),
        nullable=False
    )

    payload = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )