from app.db.database import SessionLocal
from app.services.usage_service import UsageService


def test_same_idempotency_key_returns_same_event():
    db = SessionLocal()

    try:
        key = "pytest-same-key-001"

        first = UsageService.record_usage(
            db=db,
            tenant_id=1,
            metric="api_calls",
            quantity=1,
            idempotency_key=key
        )

        second = UsageService.record_usage(
            db=db,
            tenant_id=1,
            metric="api_calls",
            quantity=1,
            idempotency_key=key
        )

        assert first.id == second.id

    finally:
        db.close()


def test_different_idempotency_keys_create_different_events():
    db = SessionLocal()

    try:
        first = UsageService.record_usage(
            db=db,
            tenant_id=1,
            metric="api_calls",
            quantity=1,
            idempotency_key="pytest-different-key-A"
        )

        second = UsageService.record_usage(
            db=db,
            tenant_id=1,
            metric="api_calls",
            quantity=1,
            idempotency_key="pytest-different-key-B"
        )

        assert first.id != second.id

    finally:
        db.close()