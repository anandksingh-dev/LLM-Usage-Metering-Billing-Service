from app.db.database import SessionLocal
from app.services.quota_service import (
    QuotaService,
    QuotaExceededError
)

db = SessionLocal()

try:
    print("Testing API call quota...")

    # Test a normal request
    result = QuotaService.check_quota(
        db=db,
        tenant_id=1,
        metric="api_calls",
        quantity=1
    )

    print("Normal request:")
    print(result)

    # Test a request that would exceed the quota
    try:
        result = QuotaService.check_quota(
            db=db,
            tenant_id=1,
            metric="api_calls",
            quantity=1000
        )

        print("Large request:")
        print(result)

    except QuotaExceededError as e:
        print("Quota correctly rejected:")
        print(e)

finally:
    db.close()