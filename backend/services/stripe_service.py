import os
from typing import Any

import stripe
from sqlalchemy.orm import Session

from backend.models import Subscription, SubscriptionTier, SubscriptionStatus


stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

TIER_TO_PRICE_ID: dict[SubscriptionTier, str] = {
    SubscriptionTier.PRO: os.getenv("STRIPE_PRO_PRICE_ID", ""),
    SubscriptionTier.FAMILY: os.getenv("STRIPE_FAMILY_PRICE_ID", ""),
}


def get_or_create_customer(db: Session, user_id: str, email: str | None = None) -> str:
    sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()

    if sub and sub.stripe_customer_id:
        return sub.stripe_customer_id

    customer = stripe.Customer.create(
        metadata={"user_id": user_id},
        email=email,
    )

    if not sub:
        sub = Subscription(user_id=user_id, stripe_customer_id=customer.id)
        db.add(sub)
    else:
        sub.stripe_customer_id = customer.id

    db.commit()
    return customer.id


def create_checkout_session(
    db: Session,
    user_id: str,
    tier: SubscriptionTier,
    success_url: str,
    cancel_url: str,
    email: str | None = None,
) -> str:
    if tier == SubscriptionTier.FREE:
        raise ValueError("Cannot checkout for free tier")

    customer_id = get_or_create_customer(db, user_id, email)
    price_id = TIER_TO_PRICE_ID.get(tier)

    if not price_id:
        raise ValueError(f"No price configured for tier: {tier}")

    checkout_session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"user_id": user_id, "tier": tier.value},
    )

    return checkout_session.url or ""


def create_portal_session(db: Session, user_id: str, return_url: str) -> str:
    sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()

    if not sub or not sub.stripe_customer_id:
        raise ValueError("No subscription found for user")

    portal_session = stripe.billing_portal.Session.create(
        customer=sub.stripe_customer_id,
        return_url=return_url,
    )

    return portal_session.url


def verify_webhook_signature(payload: bytes, signature: str) -> dict[str, Any]:
    return stripe.Webhook.construct_event(payload, signature, STRIPE_WEBHOOK_SECRET)


def handle_checkout_completed(db: Session, event_data: dict[str, Any]) -> None:
    session = event_data.get("object", {})
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")
    metadata = session.get("metadata", {})
    tier_str = metadata.get("tier", "pro")

    tier = (
        SubscriptionTier(tier_str)
        if tier_str in [t.value for t in SubscriptionTier]
        else SubscriptionTier.PRO
    )

    sub = db.query(Subscription).filter(Subscription.stripe_customer_id == customer_id).first()
    if sub:
        sub.stripe_subscription_id = subscription_id
        sub.tier = tier
        sub.status = SubscriptionStatus.ACTIVE
        db.commit()


def handle_subscription_updated(db: Session, event_data: dict[str, Any]) -> None:
    subscription = event_data.get("object", {})
    subscription_id = subscription.get("id")
    status = subscription.get("status")
    current_period_end = subscription.get("current_period_end")

    sub = (
        db.query(Subscription)
        .filter(Subscription.stripe_subscription_id == subscription_id)
        .first()
    )
    if not sub:
        return

    status_map = {
        "active": SubscriptionStatus.ACTIVE,
        "canceled": SubscriptionStatus.CANCELED,
        "past_due": SubscriptionStatus.PAST_DUE,
        "unpaid": SubscriptionStatus.UNPAID,
        "trialing": SubscriptionStatus.TRIALING,
    }
    sub.status = status_map.get(status, SubscriptionStatus.ACTIVE)

    if current_period_end:
        from datetime import datetime, timezone

        sub.current_period_end = datetime.fromtimestamp(current_period_end, tz=timezone.utc)

    db.commit()


def handle_subscription_deleted(db: Session, event_data: dict[str, Any]) -> None:
    subscription = event_data.get("object", {})
    subscription_id = subscription.get("id")

    sub = (
        db.query(Subscription)
        .filter(Subscription.stripe_subscription_id == subscription_id)
        .first()
    )
    if sub:
        sub.tier = SubscriptionTier.FREE
        sub.status = SubscriptionStatus.CANCELED
        sub.stripe_subscription_id = None
        db.commit()
