from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from app.models.plan import Plan
from app.services.usage_service import UsageService


class QuotaExceededError(Exception):
    pass


class QuotaService:

    @staticmethod
    def get_metric_limit(plan: Plan, metric: str) -> int:

        if metric == "api_calls":
            return plan.api_call_limit

        if metric == "ai_tokens":
            return plan.ai_token_limit

        raise ValueError(f"Unsupported metric: {metric}")

    @staticmethod
    def check_quota(
        db: Session,
        tenant_id: int,
        metric: str,
        quantity: int
    ):

        # Find the tenant's active subscription
        subscription = (
            db.query(Subscription)
            .filter(
                Subscription.tenant_id == tenant_id,
                Subscription.status == "active"
            )
            .first()
        )

        if not subscription:
            raise ValueError(
                "Tenant does not have an active subscription"
            )

        # Get the subscribed plan
        plan = (
            db.query(Plan)
            .filter(Plan.id == subscription.plan_id)
            .first()
        )

        if not plan:
            raise ValueError(
                "Subscription plan not found"
            )

        # Get the monthly limit
        limit = QuotaService.get_metric_limit(
            plan,
            metric
        )

        # Get current monthly usage
        current_usage = UsageService.get_current_usage(
            db,
            tenant_id,
            metric
        )

        # Check whether the new usage would exceed the limit
        if current_usage + quantity > limit:
            raise QuotaExceededError(
                f"Quota exceeded for {metric}. "
                f"Current usage: {current_usage}, "
                f"Requested: {quantity}, "
                f"Limit: {limit}"
            )

        return {
            "allowed": True,
            "current_usage": current_usage,
            "requested": quantity,
            "limit": limit,
            "remaining": limit - current_usage - quantity
        }