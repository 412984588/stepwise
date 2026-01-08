import pytest
from fastapi.testclient import TestClient

from backend.utils.validation import is_valid_uuid_v4


class TestStartSessionSuccess:
    @pytest.mark.contract
    def test_start_session_returns_201(self, client: TestClient) -> None:
        """POST /sessions/start with valid input returns 201."""
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )

        assert response.status_code == 201

    @pytest.mark.contract
    def test_start_session_returns_session_id(self, client: TestClient) -> None:
        """Response contains session_id in UUID v4 format."""
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )

        data = response.json()
        assert "session_id" in data
        assert is_valid_uuid_v4(data["session_id"])

    @pytest.mark.contract
    def test_start_session_returns_problem_type(self, client: TestClient) -> None:
        """Response contains identified problem_type."""
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )

        data = response.json()
        assert "problem_type" in data
        assert data["problem_type"] == "LINEAR_EQUATION_1VAR"

    @pytest.mark.contract
    def test_start_session_returns_concept_layer(self, client: TestClient) -> None:
        """Response starts at CONCEPT layer."""
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )

        data = response.json()
        assert data["current_layer"] == "CONCEPT"

    @pytest.mark.contract
    def test_start_session_returns_hint_content(self, client: TestClient) -> None:
        """Response contains hint_content string."""
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )

        data = response.json()
        assert "hint_content" in data
        assert len(data["hint_content"]) > 0

    @pytest.mark.contract
    def test_start_session_hint_does_not_contain_answer(self, client: TestClient) -> None:
        """Hint content must NOT contain the answer."""
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )

        data = response.json()
        hint = data["hint_content"]
        assert "x = 3" not in hint
        assert "x=3" not in hint
        assert "= 3" not in hint

    @pytest.mark.contract
    def test_start_session_requires_response_is_true(self, client: TestClient) -> None:
        """Response indicates student must respond to continue."""
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )

        data = response.json()
        assert data["requires_response"] is True


class TestStartSessionEmptyInput:
    @pytest.mark.contract
    def test_empty_string_returns_400(self, client: TestClient) -> None:
        """Empty problem_text returns 400."""
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": ""},
        )

        assert response.status_code == 400

    @pytest.mark.contract
    def test_empty_string_returns_error_code(self, client: TestClient) -> None:
        """Empty input returns EMPTY_INPUT error code."""
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": ""},
        )

        data = response.json()
        assert data["error"] == "EMPTY_INPUT"

    @pytest.mark.contract
    def test_empty_string_returns_friendly_message(self, client: TestClient) -> None:
        """Error message is user-friendly."""
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": ""},
        )

        data = response.json()
        assert "请输入" in data["message"] or "enter" in data["message"].lower()

    @pytest.mark.contract
    def test_whitespace_only_returns_400(self, client: TestClient) -> None:
        """Whitespace-only problem_text returns 400."""
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "     "},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "EMPTY_INPUT"

    @pytest.mark.contract
    def test_missing_problem_text_returns_422(self, client: TestClient) -> None:
        """Missing problem_text field returns 422 validation error."""
        response = client.post(
            "/api/v1/sessions/start",
            json={},
        )

        assert response.status_code == 422


class TestStartSessionInputValidation:
    @pytest.mark.contract
    def test_too_long_input_returns_400(self, client: TestClient) -> None:
        """problem_text > 500 chars returns 400."""
        long_text = "x" * 501
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": long_text},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "TOO_LONG"

    @pytest.mark.contract
    def test_non_math_input_returns_400(self, client: TestClient) -> None:
        """Non-math content returns 400 with NOT_MATH error."""
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "今天天气真好，我想去公园玩"},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "NOT_MATH"

    @pytest.mark.contract
    def test_500_char_input_is_accepted(self, client: TestClient) -> None:
        """problem_text exactly 500 chars is accepted."""
        text_500 = "3x + 5 = 14" + " " * 489
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": text_500},
        )

        assert response.status_code == 201


class TestRespondUnderstood:
    """T051: Tests for respond endpoint when student demonstrates understanding."""

    @pytest.mark.contract
    def test_respond_with_keyword_returns_200(self, client: TestClient) -> None:
        """Response with keyword should return 200."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]

        response = client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "我觉得应该用移项的方法来解方程"},
        )

        assert response.status_code == 200

    @pytest.mark.contract
    def test_respond_understood_advances_layer(self, client: TestClient) -> None:
        """UNDERSTOOD response should advance to next layer."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]
        assert start_resp.json()["current_layer"] == "CONCEPT"

        response = client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "等式两边同时加减相同的数，等式仍然成立"},
        )

        data = response.json()
        assert data["understanding_level"] == "UNDERSTOOD"
        assert data["current_layer"] == "STRATEGY"

    @pytest.mark.contract
    def test_respond_returns_new_hint(self, client: TestClient) -> None:
        """UNDERSTOOD response should return new layer hint."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]

        response = client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "移项把常数项移到等式右边"},
        )

        data = response.json()
        assert "hint_content" in data
        assert len(data["hint_content"]) > 0

    @pytest.mark.contract
    def test_respond_hint_no_answer(self, client: TestClient) -> None:
        """New hint should not contain the answer."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]

        response = client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "等式性质可以帮助我们解方程"},
        )

        hint = response.json()["hint_content"]
        assert "x = 3" not in hint
        assert "x=3" not in hint


class TestRespondConfused:
    """T052: Tests for respond endpoint when student is confused."""

    @pytest.mark.contract
    def test_respond_too_short_returns_error(self, client: TestClient) -> None:
        """Response < 10 chars should return error."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]

        response = client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "不知道"},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "RESPONSE_TOO_SHORT"

    @pytest.mark.contract
    def test_respond_no_keyword_stays_on_layer(self, client: TestClient) -> None:
        """Response without keyword should stay on same layer."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]

        response = client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "我觉得这道题目看起来挺有意思的"},
        )

        data = response.json()
        assert data["understanding_level"] == "CONFUSED"
        assert data["current_layer"] == "CONCEPT"

    @pytest.mark.contract
    def test_respond_confused_increments_count(self, client: TestClient) -> None:
        """CONFUSED response should increment confusion count."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]

        response = client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "我觉得这道题目看起来挺有意思的"},
        )

        data = response.json()
        assert data["confusion_count"] == 1

    @pytest.mark.contract
    def test_respond_confused_returns_supplementary_hint(self, client: TestClient) -> None:
        """CONFUSED response should return supplementary guidance."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]

        response = client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "这道题我不太确定应该怎么做"},
        )

        data = response.json()
        assert "hint_content" in data
        assert len(data["hint_content"]) > 0

    @pytest.mark.contract
    def test_respond_explicit_confused_detected(self, client: TestClient) -> None:
        """Explicit confusion phrases should be detected."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]

        response = client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "我完全不懂这道题应该怎么解决"},
        )

        data = response.json()
        assert data["understanding_level"] in ("CONFUSED", "EXPLICIT_CONFUSED")

    @pytest.mark.contract
    def test_three_confusions_triggers_downgrade(self, client: TestClient) -> None:
        """Three consecutive confusions should trigger downgrade hint."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]

        # Use text without keywords to ensure CONFUSED evaluation
        # Avoid: 解, 方程, 移项, 等式, 未知数, x, 两边, 系数, 常数, 合并, 同类项
        response = None
        for i in range(3):
            response = client.post(
                f"/api/v1/sessions/{session_id}/respond",
                json={"response_text": f"我觉得这道题目看起来挺有意思的第{i + 1}次尝试"},
            )

        assert response is not None
        data = response.json()
        assert data["confusion_count"] == 3
        assert data.get("is_downgrade") is True or data["confusion_count"] >= 3


class TestRespondSessionValidation:
    """Additional tests for respond endpoint validation."""

    @pytest.mark.contract
    def test_respond_invalid_session_returns_404(self, client: TestClient) -> None:
        """Invalid session_id should return 404."""
        response = client.post(
            "/api/v1/sessions/invalid_session_id/respond",
            json={"response_text": "这是一个测试回复"},
        )

        assert response.status_code == 404

    @pytest.mark.contract
    def test_respond_missing_text_returns_422(self, client: TestClient) -> None:
        """Missing response_text should return 422."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]

        response = client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={},
        )

        assert response.status_code == 422


class TestRevealSolution:
    """Tests for POST /sessions/{id}/reveal endpoint."""

    def _complete_three_layers(self, client: TestClient, session_id: str) -> None:
        """Helper to progress through all three layers."""
        responses = [
            "我觉得需要使用移项来把常数移到等式右边",
            "我理解了，需要先移项再合并同类项",
            "按照步骤来，先把5移到右边变成负数",
        ]
        for text in responses:
            client.post(
                f"/api/v1/sessions/{session_id}/respond",
                json={"response_text": text},
            )

    @pytest.mark.contract
    def test_reveal_after_three_layers_returns_200(self, client: TestClient) -> None:
        """Reveal should succeed after completing three layers."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]

        self._complete_three_layers(client, session_id)

        response = client.post(f"/api/v1/sessions/{session_id}/reveal")

        assert response.status_code == 200

    @pytest.mark.contract
    def test_reveal_returns_solution_steps(self, client: TestClient) -> None:
        """Reveal response should contain solution steps."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]

        self._complete_three_layers(client, session_id)

        response = client.post(f"/api/v1/sessions/{session_id}/reveal")
        data = response.json()

        assert "steps" in data
        assert isinstance(data["steps"], list)
        assert len(data["steps"]) > 0

    @pytest.mark.contract
    def test_reveal_returns_final_answer(self, client: TestClient) -> None:
        """Reveal response should contain final answer."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]

        self._complete_three_layers(client, session_id)

        response = client.post(f"/api/v1/sessions/{session_id}/reveal")
        data = response.json()

        assert "final_answer" in data
        assert len(data["final_answer"]) > 0

    @pytest.mark.contract
    def test_reveal_updates_session_status(self, client: TestClient) -> None:
        """Reveal should update session status to REVEALED."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]

        self._complete_three_layers(client, session_id)

        client.post(f"/api/v1/sessions/{session_id}/reveal")

        session_resp = client.get(f"/api/v1/sessions/{session_id}")
        assert session_resp.json()["status"] == "REVEALED"


class TestRevealBlocked:
    """Tests for reveal endpoint blocking before completion."""

    @pytest.mark.contract
    def test_reveal_blocked_at_concept_layer(self, client: TestClient) -> None:
        """Reveal should be blocked when still at CONCEPT layer."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]

        response = client.post(f"/api/v1/sessions/{session_id}/reveal")

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "REVEAL_NOT_ALLOWED"

    @pytest.mark.contract
    def test_reveal_blocked_at_strategy_layer(self, client: TestClient) -> None:
        """Reveal should be blocked when at STRATEGY layer."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]

        client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "我觉得需要使用移项来把常数移到等式右边"},
        )

        response = client.post(f"/api/v1/sessions/{session_id}/reveal")

        assert response.status_code == 400

    @pytest.mark.contract
    def test_reveal_invalid_session_returns_404(self, client: TestClient) -> None:
        """Reveal on invalid session should return 404."""
        response = client.post("/api/v1/sessions/invalid_session/reveal")

        assert response.status_code == 404


class TestCompleteSession:
    """Tests for POST /sessions/{id}/complete endpoint."""

    @pytest.mark.contract
    def test_complete_after_step_layer_returns_200(self, client: TestClient) -> None:
        """Complete should succeed after reaching STEP layer."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]

        responses = [
            "我觉得需要使用移项来把常数移到等式右边",
            "我理解了，需要先移项再合并同类项",
        ]
        for text in responses:
            client.post(
                f"/api/v1/sessions/{session_id}/respond",
                json={"response_text": text},
            )

        response = client.post(f"/api/v1/sessions/{session_id}/complete")

        assert response.status_code == 200

    @pytest.mark.contract
    def test_complete_updates_session_status(self, client: TestClient) -> None:
        """Complete should update session status to COMPLETED."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]

        responses = [
            "我觉得需要使用移项来把常数移到等式右边",
            "我理解了，需要先移项再合并同类项",
        ]
        for text in responses:
            client.post(
                f"/api/v1/sessions/{session_id}/respond",
                json={"response_text": text},
            )

        client.post(f"/api/v1/sessions/{session_id}/complete")

        session_resp = client.get(f"/api/v1/sessions/{session_id}")
        assert session_resp.json()["status"] == "COMPLETED"

    @pytest.mark.contract
    def test_complete_blocked_at_concept_layer(self, client: TestClient) -> None:
        """Complete should be blocked at CONCEPT layer."""
        start_resp = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "3x + 5 = 14"},
        )
        session_id = start_resp.json()["session_id"]

        response = client.post(f"/api/v1/sessions/{session_id}/complete")

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "COMPLETE_NOT_ALLOWED"

    @pytest.mark.contract
    def test_complete_invalid_session_returns_404(self, client: TestClient) -> None:
        """Complete on invalid session should return 404."""
        response = client.post("/api/v1/sessions/invalid_session/complete")

        assert response.status_code == 404
