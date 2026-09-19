from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.sql import func

from app.db.database import Base


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    tenant_id = Column(
        Integer,
        ForeignKey("tenants.id"),
        nullable=False,
        index=True
    )

    metric = Column(
        String(50),
        nullable=False,
        index=True
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    # AI token breakdown
    input_tokens = Column(
        Integer,
        nullable=True
    )

    cached_input_tokens = Column(
        Integer,
        nullable=True
    )

    output_tokens = Column(
        Integer,
        nullable=True
    )

    reasoning_tokens = Column(
        Integer,
        nullable=True
    )

    idempotency_key = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_tenant_idempotency_key"
        ),
    )