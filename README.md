# Usage Metering & Billing Engine

A multi-tenant usage metering and billing backend built with Python and FastAPI.

## Project Overview

This project provides a backend service for tracking tenant usage, enforcing quotas, calculating usage costs, and handling subscription billing.

The system supports two usage metrics:

- API calls
- AI tokens

## Features

- Multi-tenant usage tracking
- Free and Pro subscription plans
- Monthly usage quotas
- Idempotent usage events
- API usage metering
- AI token metering
- Usage cost calculation
- Cached input token pricing
- Reasoning token billing
- Stripe subscription integration
- Stripe webhook verification
- Stripe event deduplication
- Automated tests with pytest

## Plans

### Free Plan

| Resource | Limit |
|---|---:|
| API calls | 1,000/month |
| AI tokens | 100,000/month |
| Price | $0 |

### Pro Plan

The Pro plan provides higher limits than the Free plan.

Current project limits:

| Resource | Limit |
|---|---:|
| API calls | 10,000/month |
| AI tokens | 1,000,000/month |

The Pro plan is intended for tenants requiring higher usage limits.

## Usage Metering

Each usage event contains:

- Tenant ID
- Metric
- Quantity
- Idempotency key
- Creation timestamp

AI usage events additionally store:

- Input tokens
- Cached input tokens
- Output tokens
- Reasoning tokens

## Idempotency

Usage requests use an idempotency key.

The same tenant and the same idempotency key cannot create multiple usage events.

This prevents duplicate usage recording when a request is retried.

## Quota Enforcement

Before recording usage, the service checks:

```text
current usage + requested usage# Usage Metering & Billing Engine

A multi-tenant usage metering and billing backend built with Python and FastAPI.

## Project Overview

This project provides a backend service for tracking tenant usage, enforcing quotas, calculating usage costs, and handling subscription billing.

The system supports two usage metrics:

- API calls
- AI tokens

## Features

- Multi-tenant usage tracking
- Free and Pro subscription plans
- Monthly usage quotas
- Idempotent usage events
- API usage metering
- AI token metering
- Usage cost calculation
- Cached input token pricing
- Reasoning token billing
- Stripe subscription integration
- Stripe webhook verification
- Stripe event deduplication
- Automated tests with pytest

## Plans

### Free Plan

| Resource | Limit |
|---|---:|
| API calls | 1,000/month |
| AI tokens | 100,000/month |
| Price | $0 |

### Pro Plan

The Pro plan provides higher limits than the Free plan.

Current project limits:

| Resource | Limit |
|---|---:|
| API calls | 10,000/month |
| AI tokens | 1,000,000/month |

The Pro plan is intended for tenants requiring higher usage limits.

## Usage Metering

Each usage event contains:

- Tenant ID
- Metric
- Quantity
- Idempotency key
- Creation timestamp

AI usage events additionally store:

- Input tokens
- Cached input tokens
- Output tokens
- Reasoning tokens

## Idempotency

Usage requests use an idempotency key.

The same tenant and the same idempotency key cannot create multiple usage events.

This prevents duplicate usage recording when a request is retried.

## Quota Enforcement

Before recording usage, the service checks:

```text
current usage + requested usage# Usage Metering & Billing Engine

A multi-tenant usage metering and billing backend built with Python and FastAPI.

## Project Overview

This project provides a backend service for tracking tenant usage, enforcing quotas, calculating usage costs, and handling subscription billing.

The system supports two usage metrics:

- API calls
- AI tokens

## Features

- Multi-tenant usage tracking
- Free and Pro subscription plans
- Monthly usage quotas
- Idempotent usage events
- API usage metering
- AI token metering
- Usage cost calculation
- Cached input token pricing
- Reasoning token billing
- Stripe subscription integration
- Stripe webhook verification
- Stripe event deduplication
- Automated tests with pytest

## Plans

### Free Plan

| Resource | Limit |
|---|---:|
| API calls | 1,000/month |
| AI tokens | 100,000/month |
| Price | $0 |

### Pro Plan

The Pro plan provides higher limits than the Free plan.

Current project limits:

| Resource | Limit |
|---|---:|
| API calls | 10,000/month |
| AI tokens | 1,000,000/month |

The Pro plan is intended for tenants requiring higher usage limits.

## Usage Metering

Each usage event contains:

- Tenant ID
- Metric
- Quantity
- Idempotency key
- Creation timestamp

AI usage events additionally store:

- Input tokens
- Cached input tokens
- Output tokens
- Reasoning tokens

## Idempotency

Usage requests use an idempotency key.

The same tenant and the same idempotency key cannot create multiple usage events.

This prevents duplicate usage recording when a request is retried.

## Quota Enforcement

Before recording usage, the service checks:

```text
current usage + requested usage