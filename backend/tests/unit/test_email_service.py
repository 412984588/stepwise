"""Unit tests for email service."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

from backend.services.email_service import (
    EmailMessage,
    EmailService,
    ConsoleEmailProvider,
    SendGridEmailProvider,
    BaseEmailProvider,
)

try:
    import sendgrid

    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False


class TestEmailMessage:
    def test_email_message_creation(self) -> None:
        message = EmailMessage(
            recipient="test@example.com",
            subject="Test Subject",
            html_body="<p>Test Body</p>",
            from_email="sender@example.com",
        )

        assert message.recipient == "test@example.com"
        assert message.subject == "Test Subject"
        assert message.html_body == "<p>Test Body</p>"
        assert message.from_email == "sender@example.com"
        assert message.pdf_attachment is None
        assert message.pdf_filename is None

    def test_email_message_with_attachment(self) -> None:
        pdf_bytes = b"%PDF-1.4 fake pdf content"
        message = EmailMessage(
            recipient="test@example.com",
            subject="Test",
            html_body="<p>Test</p>",
            pdf_attachment=pdf_bytes,
            pdf_filename="report.pdf",
        )

        assert message.pdf_attachment == pdf_bytes
        assert message.pdf_filename == "report.pdf"


class TestConsoleEmailProvider:
    def test_send_email_returns_true(self) -> None:
        provider = ConsoleEmailProvider()
        message = EmailMessage(
            recipient="test@example.com",
            subject="Test",
            html_body="<p>Test</p>",
            from_email="sender@example.com",
        )

        result = provider.send_email(message)

        assert result is True

    def test_send_email_with_attachment(self) -> None:
        provider = ConsoleEmailProvider()
        message = EmailMessage(
            recipient="test@example.com",
            subject="Test",
            html_body="<p>Test</p>",
            from_email="sender@example.com",
            pdf_attachment=b"fake pdf",
            pdf_filename="test.pdf",
        )

        result = provider.send_email(message)

        assert result is True


class TestSendGridEmailProvider:
    @pytest.mark.skipif(not SENDGRID_AVAILABLE, reason="SendGrid not installed")
    def test_send_email_success(self) -> None:
        api_key = "test-api-key"
        provider = SendGridEmailProvider(api_key)

        message = EmailMessage(
            recipient="test@example.com",
            subject="Test",
            html_body="<p>Test</p>",
            from_email="sender@example.com",
        )

        mock_response = Mock()
        mock_response.status_code = 202

        with patch("sendgrid.SendGridAPIClient") as mock_sg_class:
            mock_sg_instance = mock_sg_class.return_value
            mock_sg_instance.send.return_value = mock_response

            result = provider.send_email(message)

        assert result is True
        mock_sg_class.assert_called_once_with(api_key)
        mock_sg_instance.send.assert_called_once()

    @pytest.mark.skipif(not SENDGRID_AVAILABLE, reason="SendGrid not installed")
    def test_send_email_with_attachment_success(self) -> None:
        api_key = "test-api-key"
        provider = SendGridEmailProvider(api_key)

        message = EmailMessage(
            recipient="test@example.com",
            subject="Test",
            html_body="<p>Test</p>",
            from_email="sender@example.com",
            pdf_attachment=b"fake pdf content",
            pdf_filename="report.pdf",
        )

        mock_response = Mock()
        mock_response.status_code = 202

        with patch("sendgrid.SendGridAPIClient") as mock_sg_class:
            mock_sg_instance = mock_sg_class.return_value
            mock_sg_instance.send.return_value = mock_response

            result = provider.send_email(message)

        assert result is True

    @pytest.mark.skipif(not SENDGRID_AVAILABLE, reason="SendGrid not installed")
    def test_send_email_failure_status(self) -> None:
        api_key = "test-api-key"
        provider = SendGridEmailProvider(api_key)

        message = EmailMessage(
            recipient="test@example.com",
            subject="Test",
            html_body="<p>Test</p>",
            from_email="sender@example.com",
        )

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.body = "Bad Request"

        with patch("sendgrid.SendGridAPIClient") as mock_sg_class:
            mock_sg_instance = mock_sg_class.return_value
            mock_sg_instance.send.return_value = mock_response

            result = provider.send_email(message)

        assert result is False

    @pytest.mark.skipif(not SENDGRID_AVAILABLE, reason="SendGrid not installed")
    def test_send_email_exception(self) -> None:
        api_key = "test-api-key"
        provider = SendGridEmailProvider(api_key)

        message = EmailMessage(
            recipient="test@example.com",
            subject="Test",
            html_body="<p>Test</p>",
            from_email="sender@example.com",
        )

        with patch("sendgrid.SendGridAPIClient") as mock_sg_class:
            mock_sg_instance = mock_sg_class.return_value
            mock_sg_instance.send.side_effect = Exception("Network error")

            result = provider.send_email(message)

        assert result is False

    def test_send_email_import_error(self) -> None:
        api_key = "test-api-key"
        provider = SendGridEmailProvider(api_key)

        message = EmailMessage(
            recipient="test@example.com",
            subject="Test",
            html_body="<p>Test</p>",
            from_email="sender@example.com",
        )

        with patch("builtins.__import__", side_effect=ImportError("No module named 'sendgrid'")):
            result = provider.send_email(message)

        assert result is False


class TestEmailService:
    def test_service_with_console_provider(self) -> None:
        provider = ConsoleEmailProvider()
        service = EmailService(provider=provider)

        assert isinstance(service.provider, ConsoleEmailProvider)

    def test_service_auto_detects_console_provider(self, monkeypatch) -> None:
        monkeypatch.delenv("EMAIL_PROVIDER", raising=False)
        service = EmailService()

        assert isinstance(service.provider, ConsoleEmailProvider)

    def test_service_auto_detects_sendgrid_provider(self, monkeypatch) -> None:
        monkeypatch.setenv("EMAIL_PROVIDER", "sendgrid")
        monkeypatch.setenv("SENDGRID_API_KEY", "test-key")

        service = EmailService()

        assert isinstance(service.provider, SendGridEmailProvider)

    def test_service_falls_back_to_console_if_no_api_key(self, monkeypatch) -> None:
        monkeypatch.setenv("EMAIL_PROVIDER", "sendgrid")
        monkeypatch.delenv("SENDGRID_API_KEY", raising=False)

        service = EmailService()

        assert isinstance(service.provider, ConsoleEmailProvider)

    def test_send_learning_report_success(self, monkeypatch) -> None:
        monkeypatch.setenv("EMAIL_FROM", "test@stepwise.com")

        mock_provider = Mock(spec=BaseEmailProvider)
        mock_provider.send_email.return_value = True

        service = EmailService(provider=mock_provider)

        summary = {
            "headline": "Great progress on Linear Equations",
            "performance_level": "Good",
            "insights": ["Understood concept layer", "Needed help on strategy"],
            "recommendation": "Practice more problems",
        }

        pdf_content = b"%PDF fake content"

        result = service.send_learning_report(
            recipient_email="parent@example.com",
            session_id="test-session-123",
            summary=summary,
            pdf_content=pdf_content,
        )

        assert result is True
        mock_provider.send_email.assert_called_once()

        call_args = mock_provider.send_email.call_args[0][0]
        assert call_args.recipient == "parent@example.com"
        assert call_args.subject == "Your child's learning report – StepWise"
        assert "Great progress on Linear Equations" in call_args.html_body
        assert call_args.pdf_attachment == pdf_content
        assert call_args.pdf_filename == "stepwise_report_test-session-123.pdf"

    def test_send_learning_report_failure(self) -> None:
        mock_provider = Mock(spec=BaseEmailProvider)
        mock_provider.send_email.return_value = False

        service = EmailService(provider=mock_provider)

        summary = {
            "headline": "Test",
            "performance_level": "Good",
            "insights": [],
            "recommendation": "Test",
        }

        result = service.send_learning_report(
            recipient_email="test@example.com",
            session_id="test-123",
            summary=summary,
            pdf_content=b"pdf",
        )

        assert result is False


class TestEmailTemplateComposition:
    def test_compose_html_with_all_fields(self, monkeypatch) -> None:
        monkeypatch.setenv("EMAIL_FROM", "test@stepwise.com")

        mock_provider = Mock(spec=BaseEmailProvider)
        mock_provider.send_email.return_value = True

        service = EmailService(provider=mock_provider)

        summary = {
            "headline": "Excellent work on Quadratic Equations",
            "performance_level": "Excellent",
            "insights": [
                "Mastered the concept quickly",
                "Applied strategy independently",
                "Solved problem with minimal hints",
            ],
            "recommendation": "Try more challenging problems to build confidence",
        }

        service.send_learning_report(
            recipient_email="test@example.com",
            session_id="test-123",
            summary=summary,
            pdf_content=b"pdf",
        )

        call_args = mock_provider.send_email.call_args[0][0]
        html = call_args.html_body

        assert "Excellent work on Quadratic Equations" in html
        assert "Excellent" in html
        assert "Mastered the concept quickly" in html
        assert "Try more challenging problems" in html
        assert "StepWise Learning Report" in html
        assert "<!DOCTYPE html>" in html

    def test_compose_html_with_needs_practice(self, monkeypatch) -> None:
        monkeypatch.setenv("EMAIL_FROM", "test@stepwise.com")

        mock_provider = Mock(spec=BaseEmailProvider)
        mock_provider.send_email.return_value = True

        service = EmailService(provider=mock_provider)

        summary = {
            "headline": "Keep practicing Linear Equations",
            "performance_level": "Needs Practice",
            "insights": ["Struggled with concept layer", "Required multiple hints"],
            "recommendation": "Review basic concepts before moving forward",
        }

        service.send_learning_report(
            recipient_email="test@example.com",
            session_id="test-123",
            summary=summary,
            pdf_content=b"pdf",
        )

        call_args = mock_provider.send_email.call_args[0][0]
        html = call_args.html_body

        assert "Needs Practice" in html
        assert "Keep practicing" in html


class TestWeeklyDigestEmail:
    @pytest.mark.unit
    def test_send_weekly_digest_success(self, monkeypatch) -> None:
        monkeypatch.setenv("EMAIL_FROM", "test@stepwise.com")

        mock_provider = Mock(spec=BaseEmailProvider)
        mock_provider.send_email.return_value = True

        service = EmailService(provider=mock_provider)

        digest_data = {
            "email": "parent@example.com",
            "period_start": "2024-01-01T00:00:00",
            "period_end": "2024-01-07T23:59:59",
            "total_sessions": 15,
            "completed_sessions": 12,
            "highest_layer_reached": "step",
            "total_time_minutes": 120,
            "reveal_usage_count": 2,
            "most_challenging_topic": "Linear Equations",
            "performance_level": "Good",
            "recommendations": [
                "Keep up the consistent practice!",
                "Try to complete more problems independently.",
            ],
        }

        result = service.send_weekly_digest(
            recipient_email="parent@example.com",
            digest_data=digest_data,
            week_start_date="2024-01-01",
        )

        assert result is True
        mock_provider.send_email.assert_called_once()

    @pytest.mark.unit
    def test_weekly_digest_html_contains_key_metrics(self, monkeypatch) -> None:
        monkeypatch.setenv("EMAIL_FROM", "test@stepwise.com")

        mock_provider = Mock(spec=BaseEmailProvider)
        mock_provider.send_email.return_value = True

        service = EmailService(provider=mock_provider)

        digest_data = {
            "total_sessions": 15,
            "completed_sessions": 12,
            "highest_layer_reached": "step",
            "total_time_minutes": 120,
            "reveal_usage_count": 2,
            "most_challenging_topic": "Linear Equations",
            "performance_level": "Good",
            "recommendations": ["Keep practicing!"],
        }

        service.send_weekly_digest("parent@example.com", digest_data, week_start_date="2024-01-01")

        call_args = mock_provider.send_email.call_args[0][0]
        html = call_args.html_body

        assert "15" in html
        assert "12" in html
        assert "step" in html
        assert "120" in html
        assert "2" in html
        assert "Linear Equations" in html
        assert "Good" in html
        assert "Keep practicing!" in html

    @pytest.mark.unit
    def test_weekly_digest_subject_line(self, monkeypatch) -> None:
        monkeypatch.setenv("EMAIL_FROM", "test@stepwise.com")

        mock_provider = Mock(spec=BaseEmailProvider)
        mock_provider.send_email.return_value = True

        service = EmailService(provider=mock_provider)

        digest_data = {
            "total_sessions": 5,
            "completed_sessions": 4,
            "highest_layer_reached": "strategy",
            "total_time_minutes": 50,
            "reveal_usage_count": 1,
            "most_challenging_topic": "Geometry",
            "performance_level": "Good",
            "recommendations": ["Continue practicing"],
        }

        service.send_weekly_digest("parent@example.com", digest_data, week_start_date="2024-01-01")

        call_args = mock_provider.send_email.call_args[0][0]

        assert call_args.subject == "Your child's weekly learning summary – StepWise"
        assert call_args.recipient == "parent@example.com"

    @pytest.mark.unit
    def test_weekly_digest_performance_colors(self, monkeypatch) -> None:
        monkeypatch.setenv("EMAIL_FROM", "test@stepwise.com")

        mock_provider = Mock(spec=BaseEmailProvider)
        mock_provider.send_email.return_value = True

        service = EmailService(provider=mock_provider)

        for performance, expected_color in [
            ("Excellent", "#22c55e"),
            ("Good", "#3b82f6"),
            ("Needs Practice", "#f59e0b"),
        ]:
            digest_data = {
                "total_sessions": 10,
                "completed_sessions": 8,
                "highest_layer_reached": "step",
                "total_time_minutes": 80,
                "reveal_usage_count": 1,
                "most_challenging_topic": "Algebra",
                "performance_level": performance,
                "recommendations": ["Keep going!"],
            }

            service.send_weekly_digest(
                "parent@example.com", digest_data, week_start_date="2024-01-01"
            )

            call_args = mock_provider.send_email.call_args[0][0]
            html = call_args.html_body

            assert expected_color in html
            assert performance in html
