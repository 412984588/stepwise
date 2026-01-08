"""Email service with pluggable provider abstraction."""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    """Email message data structure."""

    recipient: str
    subject: str
    html_body: str
    from_email: Optional[str] = None
    pdf_attachment: Optional[bytes] = None
    pdf_filename: Optional[str] = None


class BaseEmailProvider(ABC):
    """Base interface for email providers."""

    @abstractmethod
    def send_email(self, message: EmailMessage) -> bool:
        """
        Send an email message.

        Args:
            message: EmailMessage to send

        Returns:
            True if sent successfully, False otherwise
        """
        pass


class ConsoleEmailProvider(BaseEmailProvider):
    """Console email provider for development/testing."""

    def send_email(self, message: EmailMessage) -> bool:
        """
        Log email to console instead of sending.

        Args:
            message: EmailMessage to log

        Returns:
            Always True
        """
        logger.info("=" * 80)
        logger.info("📧 CONSOLE EMAIL PROVIDER (Development Mode)")
        logger.info("=" * 80)
        logger.info(f"From: {message.from_email}")
        logger.info(f"To: {message.recipient}")
        logger.info(f"Subject: {message.subject}")
        logger.info("-" * 80)
        logger.info("HTML Body:")
        logger.info(message.html_body)
        logger.info("-" * 80)
        if message.pdf_attachment:
            logger.info(
                f"PDF Attachment: {message.pdf_filename} ({len(message.pdf_attachment)} bytes)"
            )
        logger.info("=" * 80)
        return True


class SendGridEmailProvider(BaseEmailProvider):
    """SendGrid email provider for production."""

    def __init__(self, api_key: str):
        """
        Initialize SendGrid provider.

        Args:
            api_key: SendGrid API key
        """
        self.api_key = api_key

    def send_email(self, message: EmailMessage) -> bool:
        """
        Send email via SendGrid API.

        Args:
            message: EmailMessage to send

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Import sendgrid here to make it optional
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import (
                Mail,
                Attachment,
                FileContent,
                FileName,
                FileType,
                Disposition,
            )
            import base64

            # Create email
            mail = Mail(
                from_email=message.from_email,
                to_emails=message.recipient,
                subject=message.subject,
                html_content=message.html_body,
            )

            # Add PDF attachment if provided
            if message.pdf_attachment and message.pdf_filename:
                encoded_file = base64.b64encode(message.pdf_attachment).decode()
                attachment = Attachment(
                    FileContent(encoded_file),
                    FileName(message.pdf_filename),
                    FileType("application/pdf"),
                    Disposition("attachment"),
                )
                mail.attachment = attachment

            # Send via SendGrid
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(mail)

            # Check response
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {message.recipient}")
                return True
            else:
                logger.error(
                    f"Failed to send email: status_code={response.status_code}, "
                    f"body={response.body}"
                )
                return False

        except ImportError:
            logger.error("SendGrid library not installed. Install with: pip install sendgrid")
            return False
        except Exception as e:
            logger.error(f"Error sending email via SendGrid: {e}", exc_info=True)
            return False


class EmailService:
    """Main email service with provider management."""

    def __init__(self, provider: Optional[BaseEmailProvider] = None):
        """
        Initialize email service.

        Args:
            provider: Email provider to use. If None, auto-detect from environment.
        """
        if provider:
            self.provider = provider
        else:
            self.provider = self._create_provider_from_env()

    def _create_provider_from_env(self) -> BaseEmailProvider:
        """
        Create email provider based on environment configuration.

        Returns:
            Configured email provider
        """
        provider_type = os.getenv("EMAIL_PROVIDER", "console").lower()

        if provider_type == "sendgrid":
            api_key = os.getenv("SENDGRID_API_KEY")
            if not api_key:
                logger.warning(
                    "EMAIL_PROVIDER=sendgrid but SENDGRID_API_KEY not set. "
                    "Falling back to console provider."
                )
                return ConsoleEmailProvider()
            return SendGridEmailProvider(api_key)
        else:
            return ConsoleEmailProvider()

    def send_learning_report(
        self,
        recipient_email: str,
        session_id: str,
        summary: dict,
        pdf_content: bytes,
        db: Optional[object] = None,
    ) -> bool:
        """
        Send a learning report email with idempotency and abuse prevention.

        This method implements a 5-step security flow:
        1. Check email preference (suppress if disabled)
        2. Check throttle (enforce rate limits)
        3. Check idempotency (prevent duplicate sends)
        4. Create pending log entry
        5. Attempt send and update status

        Args:
            recipient_email: Email address to send to
            session_id: Session ID for the report
            summary: Learning summary dict with headline, insights, recommendation
            pdf_content: PDF report as bytes
            db: Database session (required for idempotency)

        Returns:
            True if email sent successfully or suppressed, False if failed
        """
        # If no db provided, fall back to legacy behavior (no idempotency)
        if not db:
            logger.warning(
                "Database session not provided to send_learning_report(). "
                "Idempotency and throttling disabled."
            )
            return self._send_learning_report_legacy(
                recipient_email, session_id, summary, pdf_content
            )

        # Import dependencies
        from backend.models.email_send_log import EmailSendLog, EmailType, EmailSendStatus
        from backend.services.email_throttle_service import EmailThrottleService
        from backend.services.email_preference_service import EmailPreferenceService
        from backend.utils.datetime_utils import utc_now

        # STEP 1: Check preference (suppression at send time)
        if not EmailPreferenceService.is_session_reports_enabled(db, recipient_email):
            logger.info(f"Email suppressed: session reports disabled for {recipient_email}")
            return True  # Return success to avoid breaking upstream flows

        # STEP 2: Check throttle (raises HTTPException(429) if exceeded)
        try:
            allowed, remaining = EmailThrottleService.check_and_increment_throttle(
                db, recipient_email, EmailType.SESSION_REPORT
            )
            logger.info(f"Throttle check passed: {recipient_email} has {remaining} sends remaining")
        except Exception as e:
            logger.warning(f"Throttle exceeded for {recipient_email}: {e}")
            raise  # Re-raise to return 429 to client

        # STEP 3: Check idempotency
        idempotency_key = EmailSendLog.generate_idempotency_key(
            recipient_email, EmailType.SESSION_REPORT, session_id=session_id
        )

        existing = (
            db.query(EmailSendLog)
            .filter(
                EmailSendLog.idempotency_key == idempotency_key,
                EmailSendLog.status == EmailSendStatus.SENT.value,
            )
            .first()
        )

        if existing:
            logger.info(
                f"Idempotent skip: session report already sent for {session_id} "
                f"to {recipient_email} at {existing.sent_at}"
            )
            return True  # Already sent, return success

        # STEP 4: Create pending log entry
        log = EmailSendLog(
            email=recipient_email,
            email_type=EmailType.SESSION_REPORT.value,
            session_id=session_id,
            idempotency_key=idempotency_key,
            status=EmailSendStatus.PENDING.value,
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        logger.info(f"Created pending email log: {log.id}")

        # STEP 5: Attempt send (existing email composition logic)
        try:
            # Get unsubscribe token
            preference = EmailPreferenceService.get_or_create_preference(db, recipient_email)
            base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
            unsubscribe_url = (
                f"{base_url}/api/v1/email/unsubscribe/{preference.unsubscribe_token}"
                f"?type=session_reports"
            )

            from_email = os.getenv("EMAIL_FROM", "noreply@stepwise.example.com")

            # Compose HTML email body with unsubscribe link
            html_body = self._compose_learning_report_html(summary)

            # Add unsubscribe footer
            html_body = html_body.replace(
                "</body>",
                f"""
    <div style="text-align: center; padding: 16px; margin-top: 24px; border-top: 1px solid #e2e8f0;">
        <p style="margin: 0; font-size: 11px; color: #94a3b8;">
            <a href="{unsubscribe_url}" style="color: #64748b; text-decoration: underline;">Unsubscribe from session reports</a>
        </p>
    </div>
</body>""",
            )

            # Create message
            message = EmailMessage(
                recipient=recipient_email,
                subject="Your child's learning report – StepWise",
                html_body=html_body,
                from_email=from_email,
                pdf_attachment=pdf_content,
                pdf_filename=f"stepwise_report_{session_id}.pdf",
            )

            # Send via provider
            success = self.provider.send_email(message)

            # Update log status
            if success:
                log.status = EmailSendStatus.SENT.value
                log.sent_at = utc_now()
                logger.info(f"Session report sent successfully to {recipient_email}")
            else:
                log.status = EmailSendStatus.FAILED.value
                log.error_message = "Email provider returned false"
                logger.error(f"Email provider failed for {recipient_email}")

        except Exception as e:
            log.status = EmailSendStatus.FAILED.value
            log.error_message = str(e)[:500]  # Truncate to fit column
            logger.error(f"Email send exception for {recipient_email}: {e}", exc_info=True)
            success = False

        db.commit()
        return log.status == EmailSendStatus.SENT.value

    def _send_learning_report_legacy(
        self,
        recipient_email: str,
        session_id: str,
        summary: dict,
        pdf_content: bytes,
    ) -> bool:
        """
        Legacy send method without idempotency (for backward compatibility).

        Args:
            recipient_email: Email address to send to
            session_id: Session ID for the report
            summary: Learning summary dict
            pdf_content: PDF report as bytes

        Returns:
            True if sent successfully, False otherwise
        """
        from_email = os.getenv("EMAIL_FROM", "noreply@stepwise.example.com")

        # Compose HTML email body
        html_body = self._compose_learning_report_html(summary)

        # Create message
        message = EmailMessage(
            recipient=recipient_email,
            subject="Your child's learning report – StepWise",
            html_body=html_body,
            from_email=from_email,
            pdf_attachment=pdf_content,
            pdf_filename=f"stepwise_report_{session_id}.pdf",
        )

        # Send email
        return self.provider.send_email(message)

    def send_weekly_digest(
        self,
        recipient_email: str,
        digest_data: dict,
        week_start_date: str,
        unsubscribe_token: str | None = None,
        db: Optional[object] = None,
    ) -> bool:
        """
        Send weekly digest email with idempotency and abuse prevention.

        This method implements a 5-step security flow:
        1. Check email preference (suppress if disabled)
        2. Check throttle (enforce rate limits)
        3. Check idempotency (prevent duplicate sends)
        4. Create pending log entry
        5. Attempt send and update status

        Args:
            recipient_email: Email address to send to
            digest_data: Weekly digest data dict
            week_start_date: Week start date (YYYY-MM-DD format) for idempotency
            unsubscribe_token: Unsubscribe token (optional, will be fetched if not provided)
            db: Database session (required for idempotency)

        Returns:
            True if email sent successfully or suppressed, False if failed
        """
        # If no db provided, fall back to legacy behavior (no idempotency)
        if not db:
            logger.warning(
                "Database session not provided to send_weekly_digest(). "
                "Idempotency and throttling disabled."
            )
            return self._send_weekly_digest_legacy(recipient_email, digest_data, unsubscribe_token)

        # Import dependencies
        from backend.models.email_send_log import EmailSendLog, EmailType, EmailSendStatus
        from backend.services.email_throttle_service import EmailThrottleService
        from backend.services.email_preference_service import EmailPreferenceService
        from backend.utils.datetime_utils import utc_now

        # STEP 1: Check preference (suppression at send time)
        if not EmailPreferenceService.is_weekly_digest_enabled(db, recipient_email):
            logger.info(f"Email suppressed: weekly digest disabled for {recipient_email}")
            return True  # Return success to avoid breaking upstream flows

        # STEP 2: Check throttle (raises HTTPException(429) if exceeded)
        try:
            allowed, remaining = EmailThrottleService.check_and_increment_throttle(
                db, recipient_email, EmailType.WEEKLY_DIGEST
            )
            logger.info(f"Throttle check passed: {recipient_email} has {remaining} sends remaining")
        except Exception as e:
            logger.warning(f"Throttle exceeded for {recipient_email}: {e}")
            raise  # Re-raise to return 429 to client

        # STEP 3: Check idempotency
        idempotency_key = EmailSendLog.generate_idempotency_key(
            recipient_email, EmailType.WEEKLY_DIGEST, week_start_date=week_start_date
        )

        existing = (
            db.query(EmailSendLog)
            .filter(
                EmailSendLog.idempotency_key == idempotency_key,
                EmailSendLog.status == EmailSendStatus.SENT.value,
            )
            .first()
        )

        if existing:
            logger.info(
                f"Idempotent skip: weekly digest already sent for week {week_start_date} "
                f"to {recipient_email} at {existing.sent_at}"
            )
            return True  # Already sent, return success

        # STEP 4: Create pending log entry
        log = EmailSendLog(
            email=recipient_email,
            email_type=EmailType.WEEKLY_DIGEST.value,
            week_start_date=week_start_date,
            idempotency_key=idempotency_key,
            status=EmailSendStatus.PENDING.value,
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        logger.info(f"Created pending email log: {log.id}")

        # STEP 5: Attempt send
        try:
            # Get unsubscribe token if not provided
            if not unsubscribe_token:
                preference = EmailPreferenceService.get_or_create_preference(db, recipient_email)
                unsubscribe_token = preference.unsubscribe_token

            from_email = os.getenv("EMAIL_FROM", "noreply@stepwise.example.com")

            html_body = self._compose_weekly_digest_html(digest_data, unsubscribe_token)

            message = EmailMessage(
                recipient=recipient_email,
                subject="Your child's weekly learning summary – StepWise",
                html_body=html_body,
                from_email=from_email,
            )

            # Send via provider
            success = self.provider.send_email(message)

            # Update log status
            if success:
                log.status = EmailSendStatus.SENT.value
                log.sent_at = utc_now()
                logger.info(f"Weekly digest sent successfully to {recipient_email}")
            else:
                log.status = EmailSendStatus.FAILED.value
                log.error_message = "Email provider returned false"
                logger.error(f"Email provider failed for {recipient_email}")

        except Exception as e:
            log.status = EmailSendStatus.FAILED.value
            log.error_message = str(e)[:500]  # Truncate to fit column
            logger.error(f"Email send exception for {recipient_email}: {e}", exc_info=True)
            success = False

        db.commit()
        return log.status == EmailSendStatus.SENT.value

    def _send_weekly_digest_legacy(
        self,
        recipient_email: str,
        digest_data: dict,
        unsubscribe_token: str | None = None,
    ) -> bool:
        """
        Legacy send method without idempotency (for backward compatibility).

        Args:
            recipient_email: Email address to send to
            digest_data: Weekly digest data dict
            unsubscribe_token: Unsubscribe token (optional)

        Returns:
            True if sent successfully, False otherwise
        """
        from_email = os.getenv("EMAIL_FROM", "noreply@stepwise.example.com")

        html_body = self._compose_weekly_digest_html(digest_data, unsubscribe_token)

        message = EmailMessage(
            recipient=recipient_email,
            subject="Your child's weekly learning summary – StepWise",
            html_body=html_body,
            from_email=from_email,
        )

        return self.provider.send_email(message)

    def _compose_learning_report_html(self, summary: dict) -> str:
        """
        Compose HTML email body for learning report.

        Args:
            summary: Learning summary with headline, performance_level, insights, recommendation

        Returns:
            HTML string
        """
        headline = summary.get("headline", "Learning Report")
        performance = summary.get("performance_level", "Unknown")
        insights = summary.get("insights", [])
        recommendation = summary.get("recommendation", "")

        # Performance level colors
        perf_colors = {
            "Excellent": "#22c55e",
            "Good": "#3b82f6",
            "Needs Practice": "#f59e0b",
        }
        perf_color = perf_colors.get(performance, "#6b7280")

        # Build insights HTML
        insights_html = ""
        for insight in insights:
            insights_html += f"<li style='margin-bottom: 8px;'>{insight}</li>\n"

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StepWise Learning Report</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8fafc; border-radius: 8px; padding: 24px; margin-bottom: 24px;">
        <h1 style="color: #1e293b; margin: 0 0 8px 0; font-size: 24px;">StepWise Learning Report</h1>
        <p style="color: #64748b; margin: 0; font-size: 14px;">Your child's progress summary</p>
    </div>

    <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 24px; margin-bottom: 24px;">
        <h2 style="color: #0f172a; margin: 0 0 16px 0; font-size: 20px;">{headline}</h2>

        <div style="background-color: {perf_color}15; border-left: 4px solid {perf_color}; padding: 12px 16px; margin-bottom: 20px;">
            <p style="margin: 0; color: {perf_color}; font-weight: 600;">Performance: {performance}</p>
        </div>

        <h3 style="color: #334155; margin: 0 0 12px 0; font-size: 16px;">📊 Key Insights</h3>
        <ul style="margin: 0 0 20px 0; padding-left: 20px; color: #475569;">
            {insights_html}
        </ul>

        <h3 style="color: #334155; margin: 0 0 12px 0; font-size: 16px;">💡 Recommendation</h3>
        <p style="margin: 0; color: #475569; background-color: #f1f5f9; padding: 12px; border-radius: 6px;">
            {recommendation}
        </p>
    </div>

    <div style="background-color: #f8fafc; border-radius: 8px; padding: 16px; margin-bottom: 24px;">
        <p style="margin: 0 0 8px 0; font-size: 14px; color: #64748b;">
            📎 <strong>Attached:</strong> Detailed PDF report with full session analysis
        </p>
    </div>

    <div style="text-align: center; padding: 16px; border-top: 1px solid #e2e8f0;">
        <p style="margin: 0; font-size: 12px; color: #94a3b8;">
            StepWise - Socratic Math Tutoring System<br>
            This report was generated automatically after your child completed a learning session.
        </p>
    </div>
</body>
</html>
"""
        return html.strip()

    def _compose_weekly_digest_html(
        self, digest_data: dict, unsubscribe_token: str | None = None
    ) -> str:
        total_sessions = digest_data.get("total_sessions", 0)
        completed_sessions = digest_data.get("completed_sessions", 0)
        highest_layer = digest_data.get("highest_layer_reached", "concept")
        total_time = digest_data.get("total_time_minutes", 0)
        reveal_count = digest_data.get("reveal_usage_count", 0)
        challenging_topic = digest_data.get("most_challenging_topic", "N/A")
        performance = digest_data.get("performance_level", "Good")
        recommendations = digest_data.get("recommendations", [])

        perf_colors = {
            "Excellent": "#22c55e",
            "Good": "#3b82f6",
            "Needs Practice": "#f59e0b",
        }
        perf_color = perf_colors.get(performance, "#6b7280")

        recommendations_html = ""
        for rec in recommendations:
            recommendations_html += f"<li style='margin-bottom: 8px;'>{rec}</li>\n"

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StepWise Weekly Digest</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8fafc; border-radius: 8px; padding: 24px; margin-bottom: 24px;">
        <h1 style="color: #1e293b; margin: 0 0 8px 0; font-size: 24px;">📊 Weekly Learning Digest</h1>
        <p style="color: #64748b; margin: 0; font-size: 14px;">Your child's progress over the past 7 days</p>
    </div>

    <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 24px; margin-bottom: 24px;">
        <div style="background-color: {perf_color}15; border-left: 4px solid {perf_color}; padding: 12px 16px; margin-bottom: 20px;">
            <p style="margin: 0; color: {perf_color}; font-weight: 600; font-size: 18px;">Overall Performance: {performance}</p>
        </div>

        <h3 style="color: #334155; margin: 0 0 16px 0; font-size: 16px;">📈 Key Metrics</h3>
        <ul style="margin: 0 0 20px 0; padding-left: 20px; color: #475569;">
            <li style='margin-bottom: 8px;'><strong>{total_sessions}</strong> problems attempted</li>
            <li style='margin-bottom: 8px;'><strong>{completed_sessions}</strong> problems completed independently</li>
            <li style='margin-bottom: 8px;'>Reached <strong>{highest_layer}</strong> layer</li>
            <li style='margin-bottom: 8px;'><strong>{total_time}</strong> minutes spent learning</li>
            <li style='margin-bottom: 8px;'>Used full solution <strong>{reveal_count}</strong> times</li>
            <li style='margin-bottom: 8px;'>Most challenging: <strong>{challenging_topic}</strong></li>
        </ul>

        <h3 style="color: #334155; margin: 0 0 12px 0; font-size: 16px;">💡 Recommendations</h3>
        <ul style="margin: 0; padding-left: 20px; color: #475569;">
            {recommendations_html}
        </ul>
    </div>

    <div style="background-color: #f1f5f9; border-radius: 8px; padding: 16px; margin-bottom: 24px;">
        <p style="margin: 0; font-size: 14px; color: #475569;">
            🎯 <strong>Keep up the great work!</strong> Consistent practice is the key to mastering math.
        </p>
    </div>

    <div style="text-align: center; padding: 16px; border-top: 1px solid #e2e8f0;">
        <p style="margin: 0 0 12px 0; font-size: 12px; color: #94a3b8;">
            StepWise - Socratic Math Tutoring System<br>
            This digest covers learning activity from the past 7 days.
        </p>"""

        # Add unsubscribe link if token is provided
        if unsubscribe_token:
            base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
            unsubscribe_url = f"{base_url}/api/v1/email/unsubscribe/{unsubscribe_token}"
            html += f"""
        <p style="margin: 0; font-size: 11px; color: #94a3b8;">
            <a href="{unsubscribe_url}" style="color: #64748b; text-decoration: underline;">Unsubscribe from weekly reports</a>
        </p>"""

        html += """
    </div>
</body>
</html>
"""
        return html.strip()


# Global email service instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """
    Get the global email service instance.

    Returns:
        EmailService instance
    """
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
