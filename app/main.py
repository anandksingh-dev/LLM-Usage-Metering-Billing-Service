from fastapi import FastAPI, Header, HTTPException, Depends,Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.db.database import Base, engine, SessionLocal

from app.models import (
    Plan,
    Tenant,
    Subscription,
    UsageEvent,
    StripeEvent
)

from app.services.usage_service import UsageService

from app.services.quota_service import (
    QuotaService,
    QuotaExceededError
)

from app.services.billing_service import BillingService
from app.schema import GenerateAIRequest
from app.services.stripe_service import StripeService
import stripe
from app.config import STRIPE_WEBHOOK_SECRET


# Create database tables
Base.metadata.create_all(bind=engine)


# Database dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# FastAPI application
app = FastAPI(
    title="Usage Metering & Billing Engine",
    description="FlyRank Backend Capstone",
    version="1.0.0"
)


# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Usage Metering & Billing Engine API",
        "status": "running"
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# --------------------------------------------------
# DATABASE TEST
# --------------------------------------------------

@app.get("/db-test")
def database_test(db: Session = Depends(get_db)):
    return {
        "database": "connected"
    }


# --------------------------------------------------
# API CALL GENERATION
# --------------------------------------------------

@app.post("/generate")
def generate(
    tenant_id: int,
    idempotency_key: str = Header(..., alias="Idempotency-Key")
):
    db = SessionLocal()

    try:
        # 1. Check if request was already processed
        existing_event = UsageService.find_existing_event(
            db=db,
            tenant_id=tenant_id,
            idempotency_key=idempotency_key
        )

        if existing_event:
            return {
                "message": "Request already processed",
                "event_id": existing_event.id,
                "tenant_id": existing_event.tenant_id,
                "metric": existing_event.metric,
                "quantity": existing_event.quantity,
                "idempotency_key": existing_event.idempotency_key
            }

        # 2. Check quota BEFORE billable action
        try:
            quota = QuotaService.check_quota(
                db=db,
                tenant_id=tenant_id,
                metric="api_calls",
                quantity=1
            )

        except QuotaExceededError as e:
            raise HTTPException(
                status_code=429,
                detail=str(e)
            )

        # 3. Dummy billable action
        result = "Dummy AI generation completed"

        # 4. Record usage
        event = UsageService.record_usage(
            db=db,
            tenant_id=tenant_id,
            metric="api_calls",
            quantity=1,
            idempotency_key=idempotency_key
        )

        # 5. Return response
        return {
            "message": result,
            "event_id": event.id,
            "tenant_id": tenant_id,
            "metric": "api_calls",
            "quantity": 1,
            "remaining_quota": quota["remaining"]
        }

    finally:
        db.close()


# --------------------------------------------------
# AI TOKEN GENERATION
# --------------------------------------------------

@app.post("/generate-ai")
def generate_ai(
    request: GenerateAIRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key")
):
    db = SessionLocal()

    try:
        # 1. Check if request was already processed
        existing_event = UsageService.find_existing_event(
            db=db,
            tenant_id=request.tenant_id,
            idempotency_key=idempotency_key
        )

        if existing_event:
            return {
                "message": "Request already processed",
                "event_id": existing_event.id,
                "tenant_id": existing_event.tenant_id,
                "metric": existing_event.metric,
                "quantity": existing_event.quantity,
                "input_tokens": existing_event.input_tokens,
                "cached_input_tokens": existing_event.cached_input_tokens,
                "output_tokens": existing_event.output_tokens,
                "reasoning_tokens": existing_event.reasoning_tokens,
                "idempotency_key": existing_event.idempotency_key
            }

        # 2. Calculate total billable AI tokens
        total_tokens = (
            request.input_tokens
            + request.output_tokens
            + request.reasoning_tokens
        )

        # 3. Check AI token quota
        try:
            quota = QuotaService.check_quota(
                db=db,
                tenant_id=request.tenant_id,
                metric="ai_tokens",
                quantity=total_tokens
            )

        except QuotaExceededError as e:
            raise HTTPException(
                status_code=429,
                detail=str(e)
            )

        # 4. Dummy AI generation
        result = "Dummy AI generation completed"

        # 5. Record detailed AI token usage
        event = UsageService.record_usage(
            db=db,
            tenant_id=request.tenant_id,
            metric="ai_tokens",
            quantity=total_tokens,
            idempotency_key=idempotency_key,
            input_tokens=request.input_tokens,
            cached_input_tokens=request.cached_input_tokens,
            output_tokens=request.output_tokens,
            reasoning_tokens=request.reasoning_tokens
        )

        # 6. Return response
        return {
            "message": result,
            "event_id": event.id,
            "tenant_id": request.tenant_id,
            "metric": "ai_tokens",
            "quantity": total_tokens,
            "input_tokens": request.input_tokens,
            "cached_input_tokens": request.cached_input_tokens,
            "output_tokens": request.output_tokens,
            "reasoning_tokens": request.reasoning_tokens,
            "remaining_quota": quota["remaining"]
        }

    finally:
        db.close()


# --------------------------------------------------
# STRIPE CHECKOUT
# --------------------------------------------------

@app.post("/create-checkout")
def create_checkout(
    tenant_id: int,
    customer_email: str | None = None
):
    try:
        session = StripeService.create_checkout_session(
            tenant_id=tenant_id,
            customer_email=customer_email
        )

        return {
            "checkout_session_id": session.id,
            "checkout_url": session.url
        }

    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to create Stripe checkout session"
        )


# --------------------------------------------------
# USAGE SUMMARY
# --------------------------------------------------

@app.get("/usage")
def get_usage(
    tenant_id: int,
    db: Session = Depends(get_db)
):
    # 1. Find active subscription
    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.tenant_id == tenant_id,
            Subscription.status == "active"
        )
        .first()
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Active subscription not found"
        )

    # 2. Find plan
    plan = (
        db.query(Plan)
        .filter(
            Plan.id == subscription.plan_id
        )
        .first()
    )

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Plan not found"
        )

    # 3. Get usage
    usage = UsageService.get_usage_summary(db, tenant_id)

    api_cost = BillingService.calculate_api_cost(
        usage["api_calls"]
    )

    ai_events = UsageService.get_current_events(
        db,
        tenant_id,
        "ai_tokens"
    )

    ai_cost = sum(
        BillingService.calculate_event_cost(event)
        for event in ai_events
    )

    # 5. Return usage information
    return {
        "tenant_id": tenant_id,
        "plan": plan.name,

        "api_calls": {
            "used": usage["api_calls"],
            "limit": plan.api_call_limit,
            "cost_micro_dollars": api_cost
        },

        "ai_tokens": {
            "used": usage["ai_tokens"],
            "limit": plan.ai_token_limit
        }
    }   
# --------------------------------------------------
# STRIPE WEBHOOK
# --------------------------------------------------


@app.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    db: Session = Depends(get_db)
):
    payload = await request.body()

    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Stripe webhook secret is not configured"
        )

    if not stripe_signature:
        raise HTTPException(
            status_code=400,
            detail="Missing Stripe-Signature header"
        )

    # Verify Stripe signature
    try:
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            STRIPE_WEBHOOK_SECRET
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook payload"
        )

    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=400,
            detail="Invalid Stripe signature"
        )

    # Get event information
    event_id = event["id"]
    event_type = event["type"]

    # Check duplicate event
    existing_event = (
        db.query(StripeEvent)
        .filter(
            StripeEvent.event_id == event_id
        )
        .first()
    )

    if existing_event:
        return {
            "message": "Stripe event already processed",
            "event_id": event_id
        }

    # Save event
    stripe_event = StripeEvent(
        event_id=event_id,
        event_type=event_type,
        payload=payload.decode("utf-8")
    )

    db.add(stripe_event)
    db.commit()

    # Handle events
    if event_type == "checkout.session.completed":
        session = event["data"]["object"]

        tenant_id = session.get("metadata", {}).get("tenant_id")

        if tenant_id:
            tenant_id = int(tenant_id)

            subscription = (
                db.query(Subscription)
                .filter(
                    Subscription.tenant_id == tenant_id
                )
                .first()
            )

            pro_plan = (
                db.query(Plan)
                .filter(
                    Plan.name == "Pro"
                )
                .first()
            )

            if subscription and pro_plan:
                subscription.plan_id = pro_plan.id
                subscription.status = "active"
                subscription.stripe_customer_id = session.get("customer")
                subscription.stripe_subscription_id = session.get("subscription")

                db.commit()

    elif event_type == "customer.subscription.updated":

        stripe_subscription = event["data"]["object"]

        stripe_status = stripe_subscription.get("status")
        stripe_customer_id = stripe_subscription.get("customer")

        subscription = (
            db.query(Subscription)
            .filter(
                Subscription.stripe_customer_id == stripe_customer_id
            )
            .first()
        )

        if subscription:
            subscription.status = stripe_status

            period_start = stripe_subscription.get(
                "current_period_start"
            )

            period_end = stripe_subscription.get(
                "current_period_end"
            )

            if period_start:
                subscription.current_period_start = datetime.fromtimestamp(
                    period_start,
                    tz=timezone.utc
                )

            if period_end:
                subscription.current_period_end = datetime.fromtimestamp(
                    period_end,
                    tz=timezone.utc
                )

            db.commit()

    elif event_type == "customer.subscription.deleted":

        stripe_subscription = event["data"]["object"]

        stripe_customer_id = stripe_subscription.get("customer")

        subscription = (
            db.query(Subscription)
            .filter(
                Subscription.stripe_customer_id == stripe_customer_id
            )
            .first()
        )

        if subscription:
            subscription.status = "cancelled"
            db.commit()

    return {
        "message": "Stripe event processed",
        "event_id": event_id,
        "event_type": event_type
    }