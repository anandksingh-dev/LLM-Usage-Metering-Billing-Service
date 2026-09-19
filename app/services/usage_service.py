from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.usage_event import UsageEvent


class UsageService:

    @staticmethod
    def get_current_usage(
        db: Session,
        tenant_id: int,
        metric: str
    ) -> int:

        now = datetime.now(timezone.utc)

        start_of_month = datetime(
            now.year,
            now.month,
            1,
            tzinfo=timezone.utc
        )

        usage = (
            db.query(UsageEvent)
            .filter(
                UsageEvent.tenant_id == tenant_id,
                UsageEvent.metric == metric,
                UsageEvent.created_at >= start_of_month
            )
            .all()
        )

        return sum(event.quantity for event in usage)

    @staticmethod
    def find_existing_event(
        db: Session,
        tenant_id: int,
        idempotency_key: str
    ):

        return (
            db.query(UsageEvent)
            .filter(
                UsageEvent.tenant_id == tenant_id,
                UsageEvent.idempotency_key == idempotency_key
            )
            .first()
        )

    @staticmethod
    def record_usage(
        db: Session,
        tenant_id: int,
        metric: str,
        quantity: int,
        idempotency_key: str,
        input_tokens: int = 0,
        cached_input_tokens: int = 0,
        output_tokens: int = 0,
        reasoning_tokens: int = 0
    ):

        # First check if this request was already processed
        existing_event = UsageService.find_existing_event(
            db,
            tenant_id,
            idempotency_key
        )

        if existing_event:
            return existing_event

        # Create new usage event
        event = UsageEvent(
            tenant_id=tenant_id,
            metric=metric,
            quantity=quantity,
            idempotency_key=idempotency_key,
            input_tokens=input_tokens,
            cached_input_tokens=cached_input_tokens,
            output_tokens=output_tokens,
            reasoning_tokens=reasoning_tokens
        )

        try:
            db.add(event)
            db.commit()
            db.refresh(event)

            return event

        except IntegrityError:
            # Another request may have inserted the same
            # idempotency key at the same time.
            db.rollback()

            existing_event = UsageService.find_existing_event(
                db,
                tenant_id,
                idempotency_key
            )

            if existing_event:
                return existing_event

            raise

    @staticmethod
    def get_usage_summary(
        db: Session,
        tenant_id: int
    ):

        api_used = UsageService.get_current_usage(
            db,
            tenant_id,
            "api_calls"
        )

        ai_used = UsageService.get_current_usage(
            db,
            tenant_id,
            "ai_tokens"
        )

        return {
            "api_calls": api_used,
            "ai_tokens": ai_used
        }

    @staticmethod
    def get_current_events(
        db: Session,
        tenant_id: int,
        metric: str
    ):

        now = datetime.now(timezone.utc)

        start_of_month = datetime(
            now.year,
            now.month,
            1,
            tzinfo=timezone.utc
        )

        return (
            db.query(UsageEvent)
            .filter(
                UsageEvent.tenant_id == tenant_id,
                UsageEvent.metric == metric,
                UsageEvent.created_at >= start_of_month
            )
            .all()
        )