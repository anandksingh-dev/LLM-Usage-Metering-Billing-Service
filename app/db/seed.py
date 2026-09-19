from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.plan import Plan


def seed_plans():
    db: Session = SessionLocal()

    try:
        existing_plans = db.query(Plan).count()

        if existing_plans > 0:
            print("Plans already exist. Nothing to seed.")
            return

        free_plan = Plan(
            name="Free",
            api_call_limit=1000,
            ai_token_limit=100000,
            price_cents=0
        )

        pro_plan = Plan(
            name="Pro",
            api_call_limit=10000,
            ai_token_limit=1000000,
            price_cents=4900
        )

        db.add(free_plan)
        db.add(pro_plan)

        db.commit()

        print("Plans seeded successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_plans()