"""Email preference management service."""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.models.email_preference import EmailPreference


class EmailPreferenceService:
    """Service for managing email subscription preferences."""

    @staticmethod
    def get_or_create_preference(db: Session, email: str) -> EmailPreference:
        """
        Get existing preference or create a new one with weekly digest enabled by default.

        Args:
            db: Database session
            email: Email address

        Returns:
            EmailPreference instance
        """
        # Try to find existing preference
        preference = db.query(EmailPreference).filter(EmailPreference.email == email).first()

        if preference:
            return preference

        # Create new preference with unique token
        token = EmailPreference.generate_token()
        preference = EmailPreference(
            email=email, weekly_digest_enabled=True, unsubscribe_token=token
        )

        db.add(preference)
        try:
            db.commit()
            db.refresh(preference)
        except IntegrityError:
            # Handle race condition - another thread created it
            db.rollback()
            preference = db.query(EmailPreference).filter(EmailPreference.email == email).first()
            if not preference:
                raise

        return preference

    @staticmethod
    def get_preference_by_token(db: Session, token: str) -> Optional[EmailPreference]:
        """
        Get email preference by unsubscribe token.

        Args:
            db: Database session
            token: Unsubscribe token

        Returns:
            EmailPreference instance or None if not found
        """
        return db.query(EmailPreference).filter(EmailPreference.unsubscribe_token == token).first()

    @staticmethod
    def mark_unsubscribed(db: Session, token: str) -> bool:
        """
        Mark email as unsubscribed from weekly digest using token.

        Args:
            db: Database session
            token: Unsubscribe token

        Returns:
            True if successful, False if token not found
        """
        preference = EmailPreferenceService.get_preference_by_token(db, token)

        if not preference:
            return False

        preference.weekly_digest_enabled = False
        db.commit()
        db.refresh(preference)

        return True

    @staticmethod
    def is_weekly_digest_enabled(db: Session, email: str) -> bool:
        """
        Check if weekly digest is enabled for an email.

        Args:
            db: Database session
            email: Email address

        Returns:
            True if enabled (default for new emails), False if explicitly disabled
        """
        preference = db.query(EmailPreference).filter(EmailPreference.email == email).first()

        # If no preference exists, weekly digest is enabled by default
        if not preference:
            return True

        return preference.weekly_digest_enabled

    @staticmethod
    def get_unsubscribe_token(db: Session, email: str) -> str:
        """
        Get unsubscribe token for an email (creates preference if doesn't exist).

        Args:
            db: Database session
            email: Email address

        Returns:
            Unsubscribe token
        """
        preference = EmailPreferenceService.get_or_create_preference(db, email)
        return preference.unsubscribe_token

    @staticmethod
    def is_session_reports_enabled(db: Session, email: str) -> bool:
        """
        Check if session reports are enabled for an email.

        Args:
            db: Database session
            email: Email address to check

        Returns:
            True if enabled, True if no preference exists (default opt-in)
        """
        preference = db.query(EmailPreference).filter_by(email=email).first()
        if not preference:
            return True  # Default: enabled for new emails
        return preference.session_reports_enabled

    @staticmethod
    def mark_session_reports_unsubscribed(db: Session, token: str) -> bool:
        """
        Disable session reports via unsubscribe token.

        Args:
            db: Database session
            token: Unsubscribe token

        Returns:
            True if successful, False if token not found
        """
        preference = EmailPreferenceService.get_preference_by_token(db, token)
        if not preference:
            return False

        preference.session_reports_enabled = False
        db.commit()

        return True

    @staticmethod
    def mark_all_unsubscribed(db: Session, token: str) -> bool:
        """
        Disable ALL email types via unsubscribe token.

        Args:
            db: Database session
            token: Unsubscribe token

        Returns:
            True if successful, False if token not found
        """
        preference = EmailPreferenceService.get_preference_by_token(db, token)
        if not preference:
            return False

        preference.weekly_digest_enabled = False
        preference.session_reports_enabled = False
        db.commit()

        return True
