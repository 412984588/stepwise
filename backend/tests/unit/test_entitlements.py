import pytest
from datetime import date, datetime, timezone
from unittest.mock import MagicMock, patch

from backend.models import SubscriptionTier, SubscriptionStatus, Subscription, UsageRecord
from backend.services.entitlements import (
    get_tier_limits,
    get_effective_tier,
    check_can_start_session,
    increment_usage,
    TierLimits,
)


class TestGetTierLimits:
    @pytest.mark.unit
    def test_free_tier_has_3_daily_problems(self) -> None:
        limits = get_tier_limits(SubscriptionTier.FREE)
        assert limits.daily_problems == 3

    @pytest.mark.unit
    def test_pro_tier_has_unlimited_problems(self) -> None:
        limits = get_tier_limits(SubscriptionTier.PRO)
        assert limits.daily_problems is None

    @pytest.mark.unit
    def test_family_tier_has_unlimited_problems(self) -> None:
        limits = get_tier_limits(SubscriptionTier.FAMILY)
        assert limits.daily_problems is None

    @pytest.mark.unit
    def test_free_tier_no_dashboard_access(self) -> None:
        limits = get_tier_limits(SubscriptionTier.FREE)
        assert limits.dashboard_access is False

    @pytest.mark.unit
    def test_pro_tier_has_dashboard_access(self) -> None:
        limits = get_tier_limits(SubscriptionTier.PRO)
        assert limits.dashboard_access is True


class TestGetEffectiveTier:
    @pytest.mark.unit
    def test_active_subscription_returns_tier(self) -> None:
        sub = MagicMock(spec=Subscription)
        sub.tier = SubscriptionTier.PRO
        sub.status = SubscriptionStatus.ACTIVE

        result = get_effective_tier(sub)
        assert result == SubscriptionTier.PRO

    @pytest.mark.unit
    def test_canceled_with_future_period_end_returns_tier(self) -> None:
        from datetime import timedelta

        sub = MagicMock(spec=Subscription)
        sub.tier = SubscriptionTier.PRO
        sub.status = SubscriptionStatus.CANCELED
        sub.current_period_end = datetime.now(timezone.utc) + timedelta(days=10)

        result = get_effective_tier(sub)
        assert result == SubscriptionTier.PRO

    @pytest.mark.unit
    def test_past_due_returns_free(self) -> None:
        sub = MagicMock(spec=Subscription)
        sub.tier = SubscriptionTier.PRO
        sub.status = SubscriptionStatus.PAST_DUE
        sub.current_period_end = None

        result = get_effective_tier(sub)
        assert result == SubscriptionTier.FREE

    @pytest.mark.unit
    def test_trialing_returns_tier(self) -> None:
        sub = MagicMock(spec=Subscription)
        sub.tier = SubscriptionTier.PRO
        sub.status = SubscriptionStatus.TRIALING

        result = get_effective_tier(sub)
        assert result == SubscriptionTier.PRO


class TestCheckCanStartSession:
    @pytest.mark.unit
    def test_free_user_under_limit_can_start(self) -> None:
        mock_db = MagicMock()
        sub = Subscription(
            user_id="user1", tier=SubscriptionTier.FREE, status=SubscriptionStatus.ACTIVE
        )
        mock_db.query.return_value.filter.return_value.first.side_effect = [sub, None]

        result = check_can_start_session(mock_db, "user1")

        assert result.can_start is True
        assert result.used == 0
        assert result.limit == 3

    @pytest.mark.unit
    def test_free_user_at_limit_cannot_start(self) -> None:
        mock_db = MagicMock()
        sub = Subscription(
            user_id="user1", tier=SubscriptionTier.FREE, status=SubscriptionStatus.ACTIVE
        )
        usage = UsageRecord(user_id="user1", usage_date=date.today(), problems_used=3)
        mock_db.query.return_value.filter.return_value.first.side_effect = [sub, usage]

        result = check_can_start_session(mock_db, "user1")

        assert result.can_start is False
        assert result.used == 3
        assert result.limit == 3
        assert result.reason == "LIMIT_REACHED"

    @pytest.mark.unit
    def test_pro_user_always_can_start(self) -> None:
        mock_db = MagicMock()
        sub = Subscription(
            user_id="user1", tier=SubscriptionTier.PRO, status=SubscriptionStatus.ACTIVE
        )
        usage = UsageRecord(user_id="user1", usage_date=date.today(), problems_used=100)
        mock_db.query.return_value.filter.return_value.first.side_effect = [sub, usage]

        result = check_can_start_session(mock_db, "user1")

        assert result.can_start is True
        assert result.limit is None


class TestIncrementUsage:
    @pytest.mark.unit
    def test_creates_new_record_if_none_exists(self) -> None:
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = increment_usage(mock_db, "user1")

        assert result == 1
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.unit
    def test_increments_existing_record(self) -> None:
        mock_db = MagicMock()
        existing = MagicMock()
        existing.problems_used = 2
        mock_db.query.return_value.filter.return_value.first.return_value = existing

        result = increment_usage(mock_db, "user1")

        assert existing.problems_used == 3
        mock_db.commit.assert_called_once()
