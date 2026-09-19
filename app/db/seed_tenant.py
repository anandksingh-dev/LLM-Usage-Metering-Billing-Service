from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.tenant import Tenant
from app.models.plan import Plan
from app.models.subscription import Subscription


def seed_tenant():
    db: Session = SessionLocal()

    try:
        existing_tenant = db.query(Tenant).first()

        if existing_tenant:
            print("Tenant already exists. Nothing to seed.")
            return

        free_plan = (
            db.query(Plan)
            .filter(Plan.name == "Free")
            .first()
        )

        if not free_plan:
            print("Free plan does not exist. Run the plan seed first.")
            return

        tenant = Tenant(
            name="Demo Company"
        )

        db.add(tenant)
        db.flush()

        subscription = Subscription(
            tenant_id=tenant.id,
            plan_id=free_plan.id,
            status="active"
        )

        db.add(subscription)
        db.commit()

        print("Demo tenant and subscription created successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_tenant()