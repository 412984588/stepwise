#!/usr/bin/env python3
"""
Script to send weekly learning digests to all parent emails.

Usage:
    python backend/scripts/send_weekly_digests.py [--days=7] [--dry-run]

Options:
    --days: Number of days to look back (default: 7)
    --dry-run: Print what would be sent without actually sending
"""

import sys
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import distinct

from backend.database.engine import SessionLocal
from backend.models.session import HintSession
from backend.services.weekly_digest import WeeklyDigestGenerator
from backend.services.email_service import EmailService
from backend.services.email_preference_service import EmailPreferenceService
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def send_weekly_digests(
    db: Session | None = None,
    email_service: EmailService | None = None,
    days: int = 7,
    dry_run: bool = False,
) -> dict:
    """
    Send weekly digests to all parent emails.

    Args:
        db: Database session (optional, creates new if not provided)
        email_service: Email service instance (optional, creates new if not provided)
        days: Number of days to look back
        dry_run: If True, preview without sending

    Returns:
        Dictionary with summary statistics
    """
    # Allow dependency injection for testing
    db_provided = db is not None
    if db is None:
        db = SessionLocal()

    if email_service is None:
        email_service = EmailService()

    digest_generator = WeeklyDigestGenerator()

    try:
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        logger.info(f"Generating weekly digests for period: {start_date} to {end_date}")

        emails_with_sessions = (
            db.query(distinct(HintSession.parent_email))
            .filter(
                HintSession.parent_email.isnot(None),
                HintSession.started_at >= start_date,
                HintSession.started_at <= end_date,
            )
            .all()
        )

        unique_emails = [email[0] for email in emails_with_sessions]
        logger.info(f"Found {len(unique_emails)} unique parent emails with activity")

        sent_count = 0
        failed_count = 0
        skipped_count = 0

        for email in unique_emails:
            try:
                # Check if weekly digest is enabled for this email
                if not EmailPreferenceService.is_weekly_digest_enabled(db, email):
                    logger.info(f"Skipping {email} - weekly digest disabled")
                    skipped_count += 1
                    continue

                digest_data = digest_generator.generate_weekly_digest(
                    db, email, start_date, end_date
                )

                if not digest_data:
                    logger.warning(f"No digest data generated for {email}")
                    skipped_count += 1
                    continue

                # Get unsubscribe token for this email
                unsubscribe_token = EmailPreferenceService.get_unsubscribe_token(db, email)

                if dry_run:
                    logger.info(f"[DRY RUN] Would send digest to {email}")
                    logger.info(f"  - {digest_data['total_sessions']} sessions")
                    logger.info(f"  - Performance: {digest_data['performance_level']}")
                    sent_count += 1
                else:
                    success = email_service.send_weekly_digest(
                        email, digest_data, unsubscribe_token
                    )
                    if success:
                        logger.info(f"✅ Sent weekly digest to {email}")
                        sent_count += 1
                    else:
                        logger.error(f"❌ Failed to send digest to {email}")
                        failed_count += 1

            except Exception as e:
                logger.error(f"Error processing digest for {email}: {e}", exc_info=True)
                failed_count += 1

        result = {
            "total_emails": len(unique_emails),
            "sent": sent_count,
            "failed": failed_count,
            "skipped": skipped_count,
            "dry_run": dry_run,
        }

        logger.info(f"Weekly digest sending completed: {result}")
        return result

    finally:
        # Only close if we created the session
        if not db_provided:
            db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Send weekly learning digests")
    parser.add_argument("--days", type=int, default=7, help="Number of days to look back")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be sent")

    args = parser.parse_args()

    result = send_weekly_digests(days=args.days, dry_run=args.dry_run)

    print("\n" + "=" * 60)
    print("WEEKLY DIGEST SUMMARY")
    print("=" * 60)
    print(f"Total parent emails found: {result['total_emails']}")
    print(f"Successfully sent: {result['sent']}")
    print(f"Failed: {result['failed']}")
    print(f"Skipped: {result['skipped']}")
    if result["dry_run"]:
        print("\n(This was a DRY RUN - no emails were actually sent)")
    print("=" * 60)
