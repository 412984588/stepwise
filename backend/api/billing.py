from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.engine import get_db
from backend.models import SubscriptionTier
from backend.services import entitlements
from backend.services import stripe_service


router = APIRouter()


class UsageResponse(BaseModel):
    used: int
    limit: int | None
    can_start: bool


class SubscriptionResponse(BaseModel):
    tier: str
    status: str
    current_period_end: str | None
    usage: UsageResponse | None = None


class CheckoutRequest(BaseModel):
    tier: str
    success_url: str
    cancel_url: str


class CheckoutResponse(BaseModel):
    url: str


class PortalRequest(BaseModel):
    return_url: str


class PortalResponse(BaseModel):
    url: str


@router.get("/subscription")
async def get_subscription(
    user_id: str = Header(..., alias="X-User-ID"),
    db: Session = Depends(get_db),
) -> SubscriptionResponse:
    sub = entitlements.get_subscription(db, user_id)
    effective_tier = entitlements.get_effective_tier(sub)
    usage_status = entitlements.check_can_start_session(db, user_id)

    return SubscriptionResponse(
        tier=effective_tier.value,
        status=sub.status.value,
        current_period_end=sub.current_period_end.isoformat() if sub.current_period_end else None,
        usage=UsageResponse(
            used=usage_status.used,
            limit=usage_status.limit,
            can_start=usage_status.can_start,
        ),
    )


@router.post("/checkout")
async def create_checkout(
    request: CheckoutRequest,
    user_id: str = Header(..., alias="X-User-ID"),
    db: Session = Depends(get_db),
) -> CheckoutResponse:
    try:
        tier = SubscriptionTier(request.tier)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_TIER", "message": "Invalid subscription tier"},
        )

    if tier == SubscriptionTier.FREE:
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_TIER", "message": "Cannot checkout for free tier"},
        )

    try:
        url = stripe_service.create_checkout_session(
            db=db,
            user_id=user_id,
            tier=tier,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
        )
        return CheckoutResponse(url=url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": "CHECKOUT_FAILED", "message": str(e)})


@router.post("/portal")
async def create_portal(
    request: PortalRequest,
    user_id: str = Header(..., alias="X-User-ID"),
    db: Session = Depends(get_db),
) -> PortalResponse:
    try:
        url = stripe_service.create_portal_session(db, user_id, request.return_url)
        return PortalResponse(url=url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": "PORTAL_FAILED", "message": str(e)})


@router.post("/webhook")
async def handle_webhook(
    request: Request,
    stripe_signature: str = Header(..., alias="Stripe-Signature"),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    payload = await request.body()

    try:
        event = stripe_service.verify_webhook_signature(payload, stripe_signature)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_SIGNATURE", "message": "Invalid webhook signature"},
        )

    event_type = event.get("type", "")
    event_data = event.get("data", {})

    if event_type == "checkout.session.completed":
        stripe_service.handle_checkout_completed(db, event_data)
    elif event_type == "customer.subscription.updated":
        stripe_service.handle_subscription_updated(db, event_data)
    elif event_type == "customer.subscription.deleted":
        stripe_service.handle_subscription_deleted(db, event_data)

    return {"status": "received"}


@router.get("/usage")
async def get_usage(
    user_id: str = Header(..., alias="X-User-ID"),
    db: Session = Depends(get_db),
) -> UsageResponse:
    usage_status = entitlements.check_can_start_session(db, user_id)
    return UsageResponse(
        used=usage_status.used,
        limit=usage_status.limit,
        can_start=usage_status.can_start,
    )
