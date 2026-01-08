from datetime import date

from sqlalchemy import Column, String, Integer, Date, DateTime, Enum as SQLEnum

from backend.models.base import BaseModel, utc_now
from backend.models.enums import SubscriptionTier, SubscriptionStatus


class Subscription(BaseModel):
    __tablename__ = "subscriptions"

    user_id = Column(String(36), nullable=False, unique=True, index=True)
    stripe_customer_id = Column(String(255), nullable=True, unique=True)
    stripe_subscription_id = Column(String(255), nullable=True, unique=True)
    tier = Column(SQLEnum(SubscriptionTier), nullable=False, default=SubscriptionTier.FREE)
    status = Column(SQLEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class UsageRecord(BaseModel):
    __tablename__ = "usage_records"

    user_id = Column(String(36), nullable=False, index=True)
    usage_date = Column(Date, nullable=False, default=date.today)
    problems_used = Column(Integer, nullable=False, default=0)

    __table_args__ = ({"sqlite_autoincrement": True},)
