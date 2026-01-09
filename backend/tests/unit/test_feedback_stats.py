"""Unit tests for feedback stats API."""

import pytest
from fastapi.testclient import TestClient

from backend.models.feedback import FeedbackItem


class TestFeedbackStatsEndpoint:
    """Tests for GET /api/v1/feedback/stats endpoint."""

    @pytest.mark.unit
    def test_stats_empty_database(self, client: TestClient, test_db) -> None:
        """Test stats endpoint with no feedback data."""
        response = client.get("/api/v1/feedback/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0
        assert data["pmf_score"] == 0.0
        assert data["pmf_breakdown"]["very_disappointed"] == 0
        assert data["pmf_breakdown"]["somewhat_disappointed"] == 0
        assert data["pmf_breakdown"]["not_disappointed"] == 0
        assert data["grade_breakdown"] == {}
        assert data["would_pay_breakdown"] == {}
        assert data["email_opt_in_rate"] == 0.0

    @pytest.mark.unit
    def test_stats_with_feedback_data(self, client: TestClient, test_db) -> None:
        """Test stats endpoint with feedback data."""
        # Create test feedback items
        feedbacks = [
            FeedbackItem(
                grade_level="grade_6",
                pmf_answer="very_disappointed",
                would_pay="yes_definitely",
                email="test1@example.com",
            ),
            FeedbackItem(
                grade_level="grade_6",
                pmf_answer="very_disappointed",
                would_pay="yes_probably",
            ),
            FeedbackItem(
                grade_level="grade_7",
                pmf_answer="somewhat_disappointed",
                email="test2@example.com",
            ),
            FeedbackItem(
                grade_level="grade_8",
                pmf_answer="not_disappointed",
            ),
        ]
        for fb in feedbacks:
            test_db.add(fb)
        test_db.commit()

        response = client.get("/api/v1/feedback/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 4
        # PMF score: 2 very_disappointed / 4 total = 50%
        assert data["pmf_score"] == 50.0
        assert data["pmf_breakdown"]["very_disappointed"] == 2
        assert data["pmf_breakdown"]["somewhat_disappointed"] == 1
        assert data["pmf_breakdown"]["not_disappointed"] == 1
        assert data["grade_breakdown"]["grade_6"] == 2
        assert data["grade_breakdown"]["grade_7"] == 1
        assert data["grade_breakdown"]["grade_8"] == 1
        assert data["would_pay_breakdown"]["yes_definitely"] == 1
        assert data["would_pay_breakdown"]["yes_probably"] == 1
        # Email opt-in: 2 with email / 4 total = 50%
        assert data["email_opt_in_rate"] == 50.0

    @pytest.mark.unit
    def test_pmf_score_calculation(self, client: TestClient, test_db) -> None:
        """Test PMF score calculation with various distributions."""
        # Create 10 feedbacks: 4 very_disappointed (40% PMF score)
        for _ in range(4):
            test_db.add(FeedbackItem(grade_level="grade_5", pmf_answer="very_disappointed"))
        for _ in range(3):
            test_db.add(FeedbackItem(grade_level="grade_5", pmf_answer="somewhat_disappointed"))
        for _ in range(3):
            test_db.add(FeedbackItem(grade_level="grade_5", pmf_answer="not_disappointed"))
        test_db.commit()

        response = client.get("/api/v1/feedback/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 10
        assert data["pmf_score"] == 40.0


class TestFeedbackListEndpoint:
    """Tests for GET /api/v1/feedback/list endpoint."""

    @pytest.mark.unit
    def test_list_empty_database(self, client: TestClient, test_db) -> None:
        """Test list endpoint with no feedback data."""
        response = client.get("/api/v1/feedback/list")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["has_more"] is False

    @pytest.mark.unit
    def test_list_with_feedback_data(self, client: TestClient, test_db) -> None:
        """Test list endpoint returns feedback items."""
        feedback = FeedbackItem(
            grade_level="grade_6",
            pmf_answer="very_disappointed",
            would_pay="yes_definitely",
            what_worked="Great hints",
            what_confused="Nothing",
            email="test@example.com",
            locale="en-US",
        )
        test_db.add(feedback)
        test_db.commit()

        response = client.get("/api/v1/feedback/list")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        item = data["items"][0]
        assert item["grade_level"] == "grade_6"
        assert item["pmf_answer"] == "very_disappointed"
        assert item["would_pay"] == "yes_definitely"
        assert item["what_worked"] == "Great hints"
        assert item["what_confused"] == "Nothing"
        assert item["email"] == "test@example.com"
        assert item["locale"] == "en-US"
        assert "id" in item
        assert "created_at" in item

    @pytest.mark.unit
    def test_list_pagination(self, client: TestClient, test_db) -> None:
        """Test list endpoint pagination."""
        # Create 25 feedback items
        for i in range(25):
            test_db.add(FeedbackItem(grade_level="grade_5", pmf_answer="very_disappointed"))
        test_db.commit()

        # First page
        response = client.get("/api/v1/feedback/list?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 25
        assert data["has_more"] is True

        # Second page
        response = client.get("/api/v1/feedback/list?limit=10&offset=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["has_more"] is True

        # Third page (partial)
        response = client.get("/api/v1/feedback/list?limit=10&offset=20")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["has_more"] is False

    @pytest.mark.unit
    def test_list_limit_max_100(self, client: TestClient, test_db) -> None:
        """Test that limit cannot exceed 100."""
        response = client.get("/api/v1/feedback/list?limit=150")

        assert response.status_code == 400
        assert "Limit cannot exceed 100" in response.text


class TestFeedbackExportEndpoint:
    """Tests for GET /api/v1/feedback/export endpoint."""

    @pytest.mark.unit
    def test_export_empty_database(self, client: TestClient, test_db) -> None:
        """Test export endpoint with no feedback data."""
        response = client.get("/api/v1/feedback/export")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        assert "feedback_export.csv" in response.headers["content-disposition"]

        # Should have header row only
        lines = response.text.strip().split("\n")
        assert len(lines) == 1
        assert "ID" in lines[0]
        assert "PMF Answer" in lines[0]

    @pytest.mark.unit
    def test_export_with_feedback_data(self, client: TestClient, test_db) -> None:
        """Test export endpoint with feedback data."""
        feedback = FeedbackItem(
            grade_level="grade_6",
            pmf_answer="very_disappointed",
            would_pay="yes_definitely",
            what_worked="Great hints",
            email="test@example.com",
        )
        test_db.add(feedback)
        test_db.commit()
        test_db.refresh(feedback)

        response = client.get("/api/v1/feedback/export")

        assert response.status_code == 200
        lines = response.text.strip().split("\n")
        assert len(lines) == 2  # Header + 1 data row

        # Check data row contains expected values
        data_row = lines[1]
        assert feedback.id in data_row
        assert "grade_6" in data_row
        assert "very_disappointed" in data_row
        assert "yes_definitely" in data_row
        assert "Great hints" in data_row
        assert "test@example.com" in data_row

    @pytest.mark.unit
    def test_export_csv_format(self, client: TestClient, test_db) -> None:
        """Test export produces valid CSV format."""
        # Create feedback with special characters
        feedback = FeedbackItem(
            grade_level="grade_7",
            pmf_answer="somewhat_disappointed",
            what_worked='Text with "quotes" and, commas',
        )
        test_db.add(feedback)
        test_db.commit()

        response = client.get("/api/v1/feedback/export")

        assert response.status_code == 200
        # CSV should handle special characters properly
        assert "somewhat_disappointed" in response.text
