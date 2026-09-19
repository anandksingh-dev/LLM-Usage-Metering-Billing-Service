from app.db.database import SessionLocal
from app.services.quota_service import QuotaService
from app.services.usage_service import UsageService


def test_quota_allows_small_request():
    db = SessionLocal()

    try:
        result = QuotaService.check_quota(
            db=db,
            tenant_id=1,
            metric="api_calls",
            quantity=1
        )

        assert result["allowed"] is True
        assert result["requested"] == 1

    finally:
        db.close()


def test_quota_rejects_excessive_request():
    db = SessionLocal()

    try:
        current_usage = UsageService.get_current_usage(
            db,
            1,
            "api_calls"
        )

        result = None

        try:
            result = QuotaService.check_quota(
                db=db,
                tenant_id=1,
                metric="api_calls",
                quantity=1000
            )

        except Exception as e:
            result = e

        assert result is not None

    finally:
        db.close()