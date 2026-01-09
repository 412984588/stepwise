"""Unit tests for feedback API and model."""

import pytest
from fastapi.testclient import TestClient

from backend.models.feedback import FeedbackItem


class TestFeedbackEndpoint:
    """Tests for POST /api/v1/feedback endpoint."""

    @pytest.mark.unit
    def test_submit_feedback_success(self, client: TestClient, test_db) -> None:
        """Test successful feedback submission."""
        response = client.post(
            "/api/v1/feedback",
            json={
                "pmf_answer": "very_disappointed",
                "grade_level": "grade_6",
                "locale": "en-US",
                "would_pay": "yes_probably",
                "what_worked": "The hints were helpful",
                "what_confused": "Nothing really",
                "email": "parent@example.com",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["message"] == "Thank you for your feedback!"

    @pytest.mark.unit
    def test_submit_feedback_minimal(self, client: TestClient, test_db) -> None:
        """Test feedback submission with only required fields."""
        response = client.post(
            "/api/v1/feedback",
            json={
                "pmf_answer": "somewhat_disappointed",
                "grade_level": "grade_4",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data

    @pytest.mark.unit
    def test_submit_feedback_invalid_pmf_answer(self, client: TestClient) -> None:
        """Test feedback with invalid PMF answer."""
        response = client.post(
            "/api/v1/feedback",
            json={
                "pmf_answer": "invalid_answer",
                "grade_level": "grade_5",
            },
        )

        assert response.status_code == 422

    @pytest.mark.unit
    def test_submit_feedback_invalid_grade_level(self, client: TestClient) -> None:
        """Test feedback with invalid grade level."""
        response = client.post(
            "/api/v1/feedback",
            json={
                "pmf_answer": "very_disappointed",
                "grade_level": "grade_10",
            },
        )

        assert response.status_code == 422

    @pytest.mark.unit
    def test_submit_feedback_invalid_would_pay(self, client: TestClient) -> None:
        """Test feedback with invalid would_pay value."""
        response = client.post(
            "/api/v1/feedback",
            json={
                "pmf_answer": "not_disappointed",
                "grade_level": "grade_7",
                "would_pay": "invalid_value",
            },
        )

        assert response.status_code == 422

    @pytest.mark.unit
    def test_submit_feedback_invalid_email(self, client: TestClient) -> None:
        """Test feedback with invalid email format."""
        response = client.post(
            "/api/v1/feedback",
            json={
                "pmf_answer": "very_disappointed",
                "grade_level": "grade_8",
                "email": "not-an-email",
            },
        )

        assert response.status_code == 422

    @pytest.mark.unit
    def test_submit_feedback_empty_email_is_allowed(self, client: TestClient, test_db) -> None:
        """Test feedback with empty email string is allowed."""
        response = client.post(
            "/api/v1/feedback",
            json={
                "pmf_answer": "very_disappointed",
                "grade_level": "grade_9",
                "email": "",
            },
        )

        assert response.status_code == 200

    @pytest.mark.unit
    def test_submit_feedback_text_truncated(self, client: TestClient, test_db) -> None:
        """Test that long text fields are truncated to 500 chars."""
        long_text = "x" * 600

        response = client.post(
            "/api/v1/feedback",
            json={
                "pmf_answer": "somewhat_disappointed",
                "grade_level": "grade_5",
                "what_worked": long_text,
            },
        )

        assert response.status_code == 200

    @pytest.mark.unit
    def test_submit_feedback_all_pmf_values(self, client: TestClient, test_db) -> None:
        """Test all valid PMF answer values."""
        for pmf_value in ["very_disappointed", "somewhat_disappointed", "not_disappointed"]:
            response = client.post(
                "/api/v1/feedback",
                json={
                    "pmf_answer": pmf_value,
                    "grade_level": "grade_6",
                },
            )
            assert response.status_code == 200, f"Failed for pmf_answer={pmf_value}"

    @pytest.mark.unit
    def test_submit_feedback_all_grade_levels(self, client: TestClient, test_db) -> None:
        """Test all valid grade level values."""
        for grade in ["grade_4", "grade_5", "grade_6", "grade_7", "grade_8", "grade_9"]:
            response = client.post(
                "/api/v1/feedback",
                json={
                    "pmf_answer": "very_disappointed",
                    "grade_level": grade,
                },
            )
            assert response.status_code == 200, f"Failed for grade_level={grade}"

    @pytest.mark.unit
    def test_submit_feedback_all_would_pay_values(self, client: TestClient, test_db) -> None:
        """Test all valid would_pay values."""
        for would_pay in [
            "yes_definitely",
            "yes_probably",
            "not_sure",
            "probably_not",
            "definitely_not",
        ]:
            response = client.post(
                "/api/v1/feedback",
                json={
                    "pmf_answer": "very_disappointed",
                    "grade_level": "grade_6",
                    "would_pay": would_pay,
                },
            )
            assert response.status_code == 200, f"Failed for would_pay={would_pay}"


class TestFeedbackModel:
    """Tests for FeedbackItem model."""

    @pytest.mark.unit
    def test_feedback_item_creation(self, test_db) -> None:
        """Test creating a FeedbackItem instance."""
        feedback = FeedbackItem(
            locale="en-US",
            grade_level="grade_6",
            pmf_answer="very_disappointed",
            would_pay="yes_probably",
            what_worked="Hints were great",
            what_confused=None,
            email="test@example.com",
        )

        test_db.add(feedback)
        test_db.commit()
        test_db.refresh(feedback)

        assert feedback.id is not None
        assert feedback.created_at is not None
        assert feedback.locale == "en-US"
        assert feedback.grade_level == "grade_6"
        assert feedback.pmf_answer == "very_disappointed"
        assert feedback.would_pay == "yes_probably"
        assert feedback.what_worked == "Hints were great"
        assert feedback.what_confused is None
        assert feedback.email == "test@example.com"

    @pytest.mark.unit
    def test_feedback_item_minimal(self, test_db) -> None:
        """Test creating a FeedbackItem with minimal fields."""
        feedback = FeedbackItem(
            grade_level="grade_4",
            pmf_answer="not_disappointed",
        )

        test_db.add(feedback)
        test_db.commit()
        test_db.refresh(feedback)

        assert feedback.id is not None
        assert feedback.locale == "en-US"  # Default value
        assert feedback.would_pay is None
        assert feedback.what_worked is None
        assert feedback.what_confused is None
        assert feedback.email is None
