from app.config import (
    API_CALL_PRICE_MICRO,
    INPUT_TOKEN_PRICE_MICRO,
    CACHED_INPUT_TOKEN_PRICE_MICRO,
    OUTPUT_TOKEN_PRICE_MICRO,
)


class BillingService:

    @staticmethod
    def calculate_api_cost(quantity: int) -> int:
        """
        Calculate API call cost in micro-dollars.
        """

        if quantity < 0:
            raise ValueError("Quantity cannot be negative")

        return quantity * API_CALL_PRICE_MICRO

    @staticmethod
    def calculate_ai_cost(
        input_tokens: int,
        cached_input_tokens: int,
        output_tokens: int,
        reasoning_tokens: int
    ) -> int:
        """
        Calculate AI token cost in micro-dollars.
        """

        if (
            input_tokens < 0
            or cached_input_tokens < 0
            or output_tokens < 0
            or reasoning_tokens < 0
        ):
            raise ValueError("Token quantities cannot be negative")

        if cached_input_tokens > input_tokens:
            raise ValueError(
                "Cached input tokens cannot exceed input tokens"
            )

        normal_input_tokens = (
            input_tokens - cached_input_tokens
        )

        input_cost = (
            normal_input_tokens
            * INPUT_TOKEN_PRICE_MICRO
        )

        cached_input_cost = (
            cached_input_tokens
            * CACHED_INPUT_TOKEN_PRICE_MICRO
        )

        output_cost = (
            output_tokens
            * OUTPUT_TOKEN_PRICE_MICRO
        )

        reasoning_cost = (
            reasoning_tokens
            * OUTPUT_TOKEN_PRICE_MICRO
        )

        return (
            input_cost
            + cached_input_cost
            + output_cost
            + reasoning_cost
        )

    @staticmethod
    def calculate_event_cost(event) -> int:
        """
        Calculate the cost of a stored usage event.
        """

        if event.metric == "api_calls":
            return BillingService.calculate_api_cost(
                event.quantity
            )

        if event.metric == "ai_tokens":
            return BillingService.calculate_ai_cost(
                input_tokens=event.input_tokens or 0,
                cached_input_tokens=event.cached_input_tokens or 0,
                output_tokens=event.output_tokens or 0,
                reasoning_tokens=event.reasoning_tokens or 0
            )

        raise ValueError(
            f"Unknown metric: {event.metric}"
        )