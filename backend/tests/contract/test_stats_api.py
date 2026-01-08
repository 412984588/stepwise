"""Contract tests for stats API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestStatsSummaryEndpoint:
    @pytest.mark.contract
    def test_returns_stats_summary(self, client: TestClient) -> None:
        response = client.get("/api/v1/stats/summary")

        assert response.status_code == 200
        data = response.json()

        assert "total_sessions" in data
        assert "completed_sessions" in data
        assert "revealed_sessions" in data
        assert "active_sessions" in data
        assert "completion_rate" in data
        assert "avg_layers_to_complete" in data

    @pytest.mark.contract
    def test_stats_types_are_correct(self, client: TestClient) -> None:
        response = client.get("/api/v1/stats/summary")
        data = response.json()

        assert isinstance(data["total_sessions"], int)
        assert isinstance(data["completed_sessions"], int)
        assert isinstance(data["revealed_sessions"], int)
        assert isinstance(data["active_sessions"], int)
        assert isinstance(data["completion_rate"], (int, float))

    @pytest.mark.contract
    def test_stats_after_creating_session(self, client: TestClient) -> None:
        initial_response = client.get("/api/v1/stats/summary")
        initial_total = initial_response.json()["total_sessions"]

        client.post("/api/v1/sessions/start", json={"problem_text": "3x + 5 = 14"})

        after_response = client.get("/api/v1/stats/summary")
        after_total = after_response.json()["total_sessions"]

        assert after_total == initial_total + 1


class TestDashboardEndpoint:
    @pytest.mark.contract
    def test_returns_dashboard_data(self, client: TestClient) -> None:
        response = client.get("/api/v1/stats/dashboard")

        assert response.status_code == 200
        data = response.json()

        assert "total_learning_days" in data
        assert "independent_completion_rate" in data
        assert "sessions_this_week" in data
        assert "learning_streak" in data
        assert "problem_type_stats" in data
        assert "recent_sessions" in data
        assert "encouragement" in data

    @pytest.mark.contract
    def test_dashboard_encouragement_messages(self, client: TestClient) -> None:
        response = client.get("/api/v1/stats/dashboard")
        data = response.json()

        assert "streak_message" in data["encouragement"]
        assert "performance_message" in data["encouragement"]

    @pytest.mark.contract
    def test_dashboard_problem_stats_after_session(self, client: TestClient) -> None:
        client.post("/api/v1/sessions/start", json={"problem_text": "3x + 5 = 14"})

        response = client.get("/api/v1/stats/dashboard")
        data = response.json()

        assert data["total_learning_days"] >= 1
        assert data["sessions_this_week"] >= 1
        assert len(data["problem_type_stats"]) > 0


class TestTrendEndpoint:
    @pytest.mark.contract
    def test_returns_trend_data(self, client: TestClient) -> None:
        response = client.get("/api/v1/stats/trend")

        assert response.status_code == 200
        data = response.json()

        assert "daily_stats" in data
        assert "period_days" in data
        assert data["period_days"] == 7
        assert len(data["daily_stats"]) == 7

    @pytest.mark.contract
    def test_trend_daily_stats_structure(self, client: TestClient) -> None:
        response = client.get("/api/v1/stats/trend")
        data = response.json()

        for day_stat in data["daily_stats"]:
            assert "date" in day_stat
            assert "total" in day_stat
            assert "completed" in day_stat
            assert "revealed" in day_stat

    @pytest.mark.contract
    def test_trend_custom_days(self, client: TestClient) -> None:
        response = client.get("/api/v1/stats/trend?days=14")
        data = response.json()

        assert data["period_days"] == 14
        assert len(data["daily_stats"]) == 14


class TestGoalsEndpoint:
    @pytest.mark.contract
    def test_returns_goal_progress(self, client: TestClient) -> None:
        response = client.get("/api/v1/stats/goals")

        assert response.status_code == 200
        data = response.json()

        assert "daily_target" in data
        assert "daily_completed" in data
        assert "daily_progress" in data
        assert "weekly_target" in data
        assert "weekly_completed" in data
        assert "weekly_progress" in data

    @pytest.mark.contract
    def test_goal_custom_targets(self, client: TestClient) -> None:
        response = client.get("/api/v1/stats/goals?daily_target=5&weekly_target=25")
        data = response.json()

        assert data["daily_target"] == 5
        assert data["weekly_target"] == 25


class TestSessionsListEndpoint:
    @pytest.mark.contract
    def test_returns_sessions_list(self, client: TestClient) -> None:
        response = client.get("/api/v1/stats/sessions")

        assert response.status_code == 200
        data = response.json()

        assert "sessions" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["sessions"], list)

    @pytest.mark.contract
    def test_pagination_params(self, client: TestClient) -> None:
        response = client.get("/api/v1/stats/sessions?limit=5&offset=0")

        assert response.status_code == 200
        data = response.json()

        assert data["limit"] == 5
        assert data["offset"] == 0

    @pytest.mark.contract
    def test_session_item_structure(self, client: TestClient) -> None:
        client.post("/api/v1/sessions/start", json={"problem_text": "x + 2 = 5"})

        response = client.get("/api/v1/stats/sessions")
        data = response.json()

        assert len(data["sessions"]) > 0
        session = data["sessions"][0]

        assert "session_id" in session
        assert "problem_text" in session
        assert "status" in session
        assert "final_layer" in session
        assert "confusion_count" in session
        assert "used_full_solution" in session
        assert "started_at" in session

    @pytest.mark.contract
    def test_sessions_ordered_by_recent_first(self, client: TestClient) -> None:
        client.post("/api/v1/sessions/start", json={"problem_text": "a = 1"})
        client.post("/api/v1/sessions/start", json={"problem_text": "b = 2"})
        client.post("/api/v1/sessions/start", json={"problem_text": "c = 3"})

        response = client.get("/api/v1/stats/sessions")
        sessions = response.json()["sessions"]

        assert sessions[0]["problem_text"] == "c = 3"
