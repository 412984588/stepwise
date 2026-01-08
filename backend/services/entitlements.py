from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session

from backend.models import Subscription, UsageRecord, SubscriptionTier, SubscriptionStatus


@dataclass
class TierLimits:
    daily_problems: int | None
    all_hint_layers: bool
    dashboard_access: bool
    max_profiles: int


TIER_LIMITS: dict[SubscriptionTier, TierLimits] = {
    SubscriptionTier.FREE: TierLimits(
        daily_problems=3,
        all_hint_layers=False,
        dashboard_access=False,
        max_profiles=1,
    ),
    SubscriptionTier.PRO: TierLimits(
        daily_problems=None,
        all_hint_layers=True,
        dashboard_access=True,
        max_profiles=1,
    ),
    SubscriptionTier.FAMILY: TierLimits(
        daily_problems=None,
        all_hint_layers=True,
        dashboard_access=True,
        max_profiles=5,
    ),
}


def get_subscription(db: Session, user_id: str) -> Subscription:
    sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if not sub:
        sub = Subscription(user_id=user_id, tier=SubscriptionTier.FREE)
        db.add(sub)
        db.commit()
        db.refresh(sub)
    return sub


def get_tier_limits(tier: SubscriptionTier) -> TierLimits:
    return TIER_LIMITS.get(tier, TIER_LIMITS[SubscriptionTier.FREE])


def get_effective_tier(sub: Subscription) -> SubscriptionTier:
    if sub.status in (SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING):
        return sub.tier
    if sub.status == SubscriptionStatus.CANCELED and sub.current_period_end:
        from datetime import datetime, timezone

        if sub.current_period_end > datetime.now(timezone.utc):
            return sub.tier
    return SubscriptionTier.FREE


def get_daily_usage(db: Session, user_id: str) -> int:
    today = date.today()
    record = (
        db.query(UsageRecord)
        .filter(
            UsageRecord.user_id == user_id,
            UsageRecord.usage_date == today,
        )
        .first()
    )
    return record.problems_used if record else 0


def increment_usage(db: Session, user_id: str) -> int:
    today = date.today()
    record = (
        db.query(UsageRecord)
        .filter(
            UsageRecord.user_id == user_id,
            UsageRecord.usage_date == today,
        )
        .first()
    )

    if record:
        record.problems_used += 1
    else:
        record = UsageRecord(user_id=user_id, usage_date=today, problems_used=1)
        db.add(record)

    db.commit()
    return record.problems_used


@dataclass
class UsageStatus:
    can_start: bool
    used: int
    limit: int | None
    tier: SubscriptionTier
    reason: str | None = None


def check_can_start_session(db: Session, user_id: str) -> UsageStatus:
    sub = get_subscription(db, user_id)
    effective_tier = get_effective_tier(sub)
    limits = get_tier_limits(effective_tier)
    used = get_daily_usage(db, user_id)

    if limits.daily_problems is None:
        return UsageStatus(
            can_start=True,
            used=used,
            limit=None,
            tier=effective_tier,
        )

    if used >= limits.daily_problems:
        return UsageStatus(
            can_start=False,
            used=used,
            limit=limits.daily_problems,
            tier=effective_tier,
            reason="LIMIT_REACHED",
        )

    return UsageStatus(
        can_start=True,
        used=used,
        limit=limits.daily_problems,
        tier=effective_tier,
    )
