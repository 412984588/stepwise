"""Unit tests for EmailPreferenceService."""

import pytest
from sqlalchemy.orm import Session

from backend.models.email_preference import EmailPreference
from backend.services.email_preference_service import EmailPreferenceService


class TestGetOrCreatePreference:
    """Tests for get_or_create_preference method."""

    @pytest.mark.unit
    def test_creates_new_preference_with_token(self, test_db: Session) -> None:
        """Should create new preference with generated token."""
        email = "parent@example.com"

        preference = EmailPreferenceService.get_or_create_preference(test_db, email)

        assert preference.email == email
        assert preference.weekly_digest_enabled is True
        assert preference.unsubscribe_token is not None
        assert len(preference.unsubscribe_token) == 36  # UUID format

    @pytest.mark.unit
    def test_returns_existing_preference(self, test_db: Session) -> None:
        """Should return existing preference if it exists."""
        email = "parent@example.com"

        # Create first preference
        pref1 = EmailPreferenceService.get_or_create_preference(test_db, email)
        token1 = pref1.unsubscribe_token

        # Get again - should return same preference
        pref2 = EmailPreferenceService.get_or_create_preference(test_db, email)

        assert pref2.email == email
        assert pref2.unsubscribe_token == token1
        assert pref2.id == pref1.id

    @pytest.mark.unit
    def test_different_emails_get_different_tokens(self, test_db: Session) -> None:
        """Should generate different tokens for different emails."""
        email1 = "parent1@example.com"
        email2 = "parent2@example.com"

        pref1 = EmailPreferenceService.get_or_create_preference(test_db, email1)
        pref2 = EmailPreferenceService.get_or_create_preference(test_db, email2)

        assert pref1.unsubscribe_token != pref2.unsubscribe_token


class TestMarkUnsubscribed:
    """Tests for mark_unsubscribed method."""

    @pytest.mark.unit
    def test_marks_preference_as_unsubscribed(self, test_db: Session) -> None:
        """Should set weekly_digest_enabled to False."""
        email = "parent@example.com"
        preference = EmailPreferenceService.get_or_create_preference(test_db, email)
        token = preference.unsubscribe_token

        # Initially enabled
        assert preference.weekly_digest_enabled is True

        # Mark as unsubscribed
        success = EmailPreferenceService.mark_unsubscribed(test_db, token)

        assert success is True

        # Check it's disabled
        test_db.refresh(preference)
        assert preference.weekly_digest_enabled is False

    @pytest.mark.unit
    def test_returns_false_for_invalid_token(self, test_db: Session) -> None:
        """Should return False if token doesn't exist."""
        invalid_token = "invalid-token-123"

        success = EmailPreferenceService.mark_unsubscribed(test_db, invalid_token)

        assert success is False

    @pytest.mark.unit
    def test_idempotent_unsubscribe(self, test_db: Session) -> None:
        """Should work correctly when called multiple times."""
        email = "parent@example.com"
        preference = EmailPreferenceService.get_or_create_preference(test_db, email)
        token = preference.unsubscribe_token

        # Unsubscribe first time
        success1 = EmailPreferenceService.mark_unsubscribed(test_db, token)
        assert success1 is True

        # Unsubscribe second time (idempotent)
        success2 = EmailPreferenceService.mark_unsubscribed(test_db, token)
        assert success2 is True

        # Still disabled
        test_db.refresh(preference)
        assert preference.weekly_digest_enabled is False


class TestIsWeeklyDigestEnabled:
    """Tests for is_weekly_digest_enabled method."""

    @pytest.mark.unit
    def test_returns_true_for_new_email(self, test_db: Session) -> None:
        """Should return True by default for emails with no preference."""
        email = "parent@example.com"

        enabled = EmailPreferenceService.is_weekly_digest_enabled(test_db, email)

        assert enabled is True

    @pytest.mark.unit
    def test_returns_true_for_enabled_preference(self, test_db: Session) -> None:
        """Should return True for explicitly enabled preference."""
        email = "parent@example.com"
        EmailPreferenceService.get_or_create_preference(test_db, email)

        enabled = EmailPreferenceService.is_weekly_digest_enabled(test_db, email)

        assert enabled is True

    @pytest.mark.unit
    def test_returns_false_for_unsubscribed_email(self, test_db: Session) -> None:
        """Should return False for unsubscribed email."""
        email = "parent@example.com"
        preference = EmailPreferenceService.get_or_create_preference(test_db, email)
        EmailPreferenceService.mark_unsubscribed(test_db, preference.unsubscribe_token)

        enabled = EmailPreferenceService.is_weekly_digest_enabled(test_db, email)

        assert enabled is False


class TestGetUnsubscribeToken:
    """Tests for get_unsubscribe_token method."""

    @pytest.mark.unit
    def test_returns_token_for_existing_preference(self, test_db: Session) -> None:
        """Should return existing token."""
        email = "parent@example.com"
        preference = EmailPreferenceService.get_or_create_preference(test_db, email)
        expected_token = preference.unsubscribe_token

        token = EmailPreferenceService.get_unsubscribe_token(test_db, email)

        assert token == expected_token

    @pytest.mark.unit
    def test_creates_preference_if_not_exists(self, test_db: Session) -> None:
        """Should create preference and return new token."""
        email = "parent@example.com"

        token = EmailPreferenceService.get_unsubscribe_token(test_db, email)

        assert token is not None
        assert len(token) == 36  # UUID format

        # Verify preference was created
        preference = test_db.query(EmailPreference).filter_by(email=email).first()
        assert preference is not None
        assert preference.unsubscribe_token == token


class TestGetPreferenceByToken:
    """Tests for get_preference_by_token method."""

    @pytest.mark.unit
    def test_returns_preference_for_valid_token(self, test_db: Session) -> None:
        """Should return preference for valid token."""
        email = "parent@example.com"
        created_pref = EmailPreferenceService.get_or_create_preference(test_db, email)
        token = created_pref.unsubscribe_token

        preference = EmailPreferenceService.get_preference_by_token(test_db, token)

        assert preference is not None
        assert preference.email == email
        assert preference.id == created_pref.id

    @pytest.mark.unit
    def test_returns_none_for_invalid_token(self, test_db: Session) -> None:
        """Should return None for invalid token."""
        invalid_token = "invalid-token-123"

        preference = EmailPreferenceService.get_preference_by_token(test_db, invalid_token)

        assert preference is None
