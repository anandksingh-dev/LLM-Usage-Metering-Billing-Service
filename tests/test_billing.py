from app.services.billing_service import BillingService


def test_api_cost():
    cost = BillingService.calculate_api_cost(100)

    assert cost == 100000


def test_ai_cost():
    cost = BillingService.calculate_ai_cost(
        input_tokens=10000,
        cached_input_tokens=2000,
        output_tokens=3000,
        reasoning_tokens=1000
    )

    assert cost == 1650000