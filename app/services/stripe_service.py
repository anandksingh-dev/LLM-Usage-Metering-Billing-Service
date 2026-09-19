import stripe

from app.config import STRIPE_SECRET_KEY, STRIPE_PRO_PRICE_ID


class StripeService:

    @staticmethod
    def create_checkout_session(
        tenant_id: int,
        customer_email: str | None = None
    ):
        if not STRIPE_SECRET_KEY:
            raise ValueError("Stripe secret key is not configured")

        if not STRIPE_PRO_PRICE_ID:
            raise ValueError("Stripe Pro price ID is not configured")

        stripe.api_key = STRIPE_SECRET_KEY

        session_data = {
            "mode": "subscription",
            "line_items": [
                {
                    "price": STRIPE_PRO_PRICE_ID,
                    "quantity": 1
                }
            ],
            "success_url": (
                "http://127.0.0.1:8000/success"
                "?session_id={CHECKOUT_SESSION_ID}"
            ),
            "cancel_url": "http://127.0.0.1:8000/cancel",
            "metadata": {
                "tenant_id": str(tenant_id)
            }
        }

        if customer_email:
            session_data["customer_email"] = customer_email

        return stripe.checkout.Session.create(**session_data)