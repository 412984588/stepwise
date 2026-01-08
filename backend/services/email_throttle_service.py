"""Email throttling service for abuse prevention."""

import logging
from datetime import datetime, timedelta
from typing import Tuple

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.email_throttle import EmailThrottle
from backend.models.email_send_log import EmailType
from backend.utils.datetime_utils import utc_now

logger = logging.getLogger(__name__)


class EmailThrottleService:
    """Service for enforcing email rate limits per recipient."""

    # Rate limits (per email address)
    SESSION_REPORT_LIMIT = 5  # per 24 hours
    WEEKLY_DIGEST_LIMIT = 1  # per 7 days

    # Window durations
    SESSION_REPORT_WINDOW = timedelta(hours=24)
    WEEKLY_DIGEST_WINDOW = timedelta(days=7)

    @staticmethod
    def _get_window_start(email_type: EmailType) -> datetime:
        """
        Get the start of the current rate limit window.

        Args:
            email_type: Type of email being sent

        Returns:
            Start of current window (truncated to hour/day boundary)
        """
        now = utc_now()

        if email_type == EmailType.SESSION_REPORT:
            # 24-hour window: truncate to start of current hour
            return now.replace(minute=0, second=0, microsecond=0)
        else:  # WEEKLY_DIGEST
            # 7-day window: truncate to start of current day
            return now.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def _get_limit(email_type: EmailType) -> int:
        """Get rate limit for email type."""
        if email_type == EmailType.SESSION_REPORT:
            return EmailThrottleService.SESSION_REPORT_LIMIT
        else:  # WEEKLY_DIGEST
            return EmailThrottleService.WEEKLY_DIGEST_LIMIT

    @staticmethod
    def check_and_increment_throttle(
        db: Session, email: str, email_type: EmailType
    ) -> Tuple[bool, int]:
        """
        Check if email is within rate limit and increment counter.

        This method is CRITICAL for abuse prevention. It:
        1. Finds or creates throttle record for current window
        2. Checks if count < limit
        3. Increments count and updates timestamp
        4. Raises HTTPException(429) if limit exceeded

        Args:
            db: Database session
            email: Recipient email address
            email_type: Type of email being sent

        Returns:
            Tuple of (allowed: bool, remaining: int)
            - allowed: Always True if no exception raised
            - remaining: Number of sends remaining in window

        Raises:
            HTTPException: 429 Too Many Requests if rate limit exceeded
        """
        window_start = EmailThrottleService._get_window_start(email_type)
        limit = EmailThrottleService._get_limit(email_type)

        # Find or create throttle record for this window
        throttle = (
            db.query(EmailThrottle)
            .filter(
                EmailThrottle.email == email,
                EmailThrottle.email_type == email_type.value,
                EmailThrottle.window_start == window_start,
            )
            .first()
        )

        if not throttle:
            # First send in this window
            throttle = EmailThrottle(
                email=email,
                email_type=email_type.value,
                window_start=window_start,
                send_count=1,
                last_send_at=utc_now(),
            )
            db.add(throttle)
            db.commit()

            remaining = limit - 1
            logger.info(
                f"Email throttle: {email} sent {email_type.value} "
                f"(1/{limit}, {remaining} remaining)"
            )
            return True, remaining

        # Check if limit exceeded
        if throttle.send_count >= limit:
            logger.warning(
                f"Email throttle EXCEEDED: {email} attempted {email_type.value} "
                f"(count={throttle.send_count}, limit={limit})"
            )

            # Calculate retry_after in seconds
            if email_type == EmailType.SESSION_REPORT:
                window_end = window_start + EmailThrottleService.SESSION_REPORT_WINDOW
            else:
                window_end = window_start + EmailThrottleService.WEEKLY_DIGEST_WINDOW

            retry_after = int((window_end - utc_now()).total_seconds())

            raise HTTPException(
                status_code=429,
                detail={
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": f"Too many {email_type.value.replace('_', ' ')}s sent. Please try again later.",
                    "retry_after": retry_after,
                    "limit": limit,
                    "window": ("24 hours" if email_type == EmailType.SESSION_REPORT else "7 days"),
                },
            )

        # Increment counter
        throttle.send_count += 1
        throttle.last_send_at = utc_now()
        db.commit()

        remaining = limit - throttle.send_count
        logger.info(
            f"Email throttle: {email} sent {email_type.value} "
            f"({throttle.send_count}/{limit}, {remaining} remaining)"
        )

        return True, remaining

    @staticmethod
    def get_remaining_sends(db: Session, email: str, email_type: EmailType) -> int:
        """
        Get number of remaining sends for an email in current window.

        Useful for showing users their remaining quota.

        Args:
            db: Database session
            email: Recipient email address
            email_type: Type of email

        Returns:
            Number of sends remaining (0 to limit)
        """
        window_start = EmailThrottleService._get_window_start(email_type)
        limit = EmailThrottleService._get_limit(email_type)

        throttle = (
            db.query(EmailThrottle)
            .filter(
                EmailThrottle.email == email,
                EmailThrottle.email_type == email_type.value,
                EmailThrottle.window_start == window_start,
            )
            .first()
        )

        if not throttle:
            return limit

        return max(0, limit - throttle.send_count)
