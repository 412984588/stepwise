"""Unit tests for StatsService - TDD approach."""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

from backend.models.enums import HintLayer, SessionStatus
from backend.services.stats_service import StatsService


class TestStatsSummaryEmpty:
    @pytest.mark.unit
    def test_returns_zeros_when_no_sessions(self) -> None:
        mock_db = MagicMock()
        mock_db.query.return_value.count.return_value = 0

        service = StatsService(mock_db)
        summary = service.get_summary()

        assert summary.total_sessions == 0
        assert summary.completed_sessions == 0
        assert summary.revealed_sessions == 0
        assert summary.completion_rate == 0.0

    @pytest.mark.unit
    def test_returns_none_for_avg_layer_when_no_sessions(self) -> None:
        mock_db = MagicMock()
        mock_db.query.return_value.count.return_value = 0

        service = StatsService(mock_db)
        summary = service.get_summary()

        assert summary.avg_layers_to_complete is None


class TestStatsSummaryWithData:
    @pytest.mark.unit
    def test_counts_total_sessions(self) -> None:
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_query.count.return_value = 10

        call_count = [0]

        def filter_side_effect(*args, **kwargs):
            result = MagicMock()
            result.count.return_value = 3
            result.all.return_value = []
            call_count[0] += 1
            return result

        mock_query.filter.side_effect = filter_side_effect

        service = StatsService(mock_db)
        summary = service.get_summary()

        assert summary.total_sessions == 10

    @pytest.mark.unit
    def test_calculates_completion_rate(self) -> None:
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_query.count.return_value = 10

        call_count = [0]

        def filter_side_effect(*args, **kwargs):
            result = MagicMock()
            if call_count[0] == 0:
                result.count.return_value = 4
            elif call_count[0] == 1:
                result.count.return_value = 2
            elif call_count[0] == 2:
                result.count.return_value = 2
            else:
                result.all.return_value = []
            result.all.return_value = []
            call_count[0] += 1
            return result

        mock_query.filter.side_effect = filter_side_effect

        service = StatsService(mock_db)
        summary = service.get_summary()

        assert summary.completion_rate == 60.0

    @pytest.mark.unit
    def test_separates_completed_and_revealed(self) -> None:
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_query.count.return_value = 10

        call_count = [0]

        def filter_side_effect(*args, **kwargs):
            result = MagicMock()
            if call_count[0] == 0:
                result.count.return_value = 4
            elif call_count[0] == 1:
                result.count.return_value = 2
            elif call_count[0] == 2:
                result.count.return_value = 2
            else:
                result.count.return_value = 0
            result.all.return_value = []
            call_count[0] += 1
            return result

        mock_query.filter.side_effect = filter_side_effect

        service = StatsService(mock_db)
        summary = service.get_summary()

        assert summary.completed_sessions == 4
        assert summary.revealed_sessions == 2


class TestSessionsList:
    @pytest.mark.unit
    def test_returns_empty_list_when_no_sessions(self) -> None:
        mock_db = MagicMock()
        mock_db.query.return_value.order_by.return_value.limit.return_value.offset.return_value.all.return_value = []

        service = StatsService(mock_db)
        sessions = service.list_sessions(limit=10, offset=0)

        assert sessions == []

    @pytest.mark.unit
    def test_returns_sessions_ordered_by_recent_first(self) -> None:
        mock_db = MagicMock()
        mock_session1 = MagicMock()
        mock_session1.id = "ses_001"
        mock_session1.started_at = datetime(2024, 1, 2, tzinfo=timezone.utc)
        mock_session1.status = SessionStatus.COMPLETED
        mock_session1.current_layer = HintLayer.COMPLETED
        mock_session1.problem.raw_text = "3x + 5 = 14"

        mock_session2 = MagicMock()
        mock_session2.id = "ses_002"
        mock_session2.started_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
        mock_session2.status = SessionStatus.ACTIVE
        mock_session2.current_layer = HintLayer.STRATEGY
        mock_session2.problem.raw_text = "x + y = 10"

        mock_db.query.return_value.order_by.return_value.limit.return_value.offset.return_value.all.return_value = [
            mock_session1,
            mock_session2,
        ]

        service = StatsService(mock_db)
        sessions = service.list_sessions(limit=10, offset=0)

        assert len(sessions) == 2
        assert sessions[0].session_id == "ses_001"
        assert sessions[1].session_id == "ses_002"

    @pytest.mark.unit
    def test_session_item_contains_required_fields(self) -> None:
        mock_db = MagicMock()
        mock_session = MagicMock()
        mock_session.id = "ses_test"
        mock_session.started_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_session.completed_at = datetime(2024, 1, 1, 12, 30, 0, tzinfo=timezone.utc)
        mock_session.status = SessionStatus.COMPLETED
        mock_session.current_layer = HintLayer.COMPLETED
        mock_session.confusion_count = 2
        mock_session.used_full_solution = False
        mock_session.problem.raw_text = "2x = 8"

        mock_db.query.return_value.order_by.return_value.limit.return_value.offset.return_value.all.return_value = [
            mock_session
        ]

        service = StatsService(mock_db)
        sessions = service.list_sessions(limit=10, offset=0)

        item = sessions[0]
        assert item.session_id == "ses_test"
        assert item.problem_text == "2x = 8"
        assert item.status == SessionStatus.COMPLETED
        assert item.final_layer == HintLayer.COMPLETED
        assert item.confusion_count == 2
        assert item.used_full_solution is False
        assert item.started_at is not None
        assert item.completed_at is not None


class TestLayerProgression:
    @pytest.mark.unit
    def test_layer_to_number_mapping(self) -> None:
        service = StatsService(MagicMock())

        assert service._layer_to_number(HintLayer.CONCEPT) == 1
        assert service._layer_to_number(HintLayer.STRATEGY) == 2
        assert service._layer_to_number(HintLayer.STEP) == 3
        assert service._layer_to_number(HintLayer.COMPLETED) == 4
        assert service._layer_to_number(HintLayer.REVEALED) == 4
