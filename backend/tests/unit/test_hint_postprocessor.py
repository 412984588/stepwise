import pytest

from backend.services.hint_postprocessor import HintPostProcessor


class TestNoNegativeWords:
    """T050: Tests that hints don't contain negative/discouraging words."""

    @pytest.mark.unit
    def test_detects_错_as_negative(self) -> None:
        """'错' should be flagged as negative word."""
        processor = HintPostProcessor()

        result = processor.process("你这样做是错的")

        assert result.was_filtered
        assert result.filter_reason == "negative_word"

    @pytest.mark.unit
    def test_detects_不对_as_negative(self) -> None:
        """'不对' should be flagged as negative word."""
        processor = HintPostProcessor()

        result = processor.process("这个答案不对，再想想")

        assert result.was_filtered
        assert result.filter_reason == "negative_word"

    @pytest.mark.unit
    def test_detects_错误_as_negative(self) -> None:
        """'错误' should be flagged as negative word."""
        processor = HintPostProcessor()

        result = processor.process("你犯了一个错误")

        assert result.was_filtered
        assert result.filter_reason == "negative_word"

    @pytest.mark.unit
    def test_detects_wrong_as_negative(self) -> None:
        """'wrong' should be flagged as negative word."""
        processor = HintPostProcessor()

        result = processor.process("That approach is wrong")

        assert result.was_filtered
        assert result.filter_reason == "negative_word"

    @pytest.mark.unit
    def test_detects_incorrect_as_negative(self) -> None:
        """'incorrect' should be flagged as negative word."""
        processor = HintPostProcessor()

        result = processor.process("This is incorrect, try again")

        assert result.was_filtered
        assert result.filter_reason == "negative_word"

    @pytest.mark.unit
    def test_encouraging_hint_passes(self) -> None:
        """Encouraging hint without negative words should pass."""
        processor = HintPostProcessor()

        result = processor.process("很好！你的思路是对的，继续思考下一步")

        assert not result.was_filtered

    @pytest.mark.unit
    def test_neutral_hint_passes(self) -> None:
        """Neutral educational hint should pass."""
        processor = HintPostProcessor()

        result = processor.process("想一想，等式的基本性质是什么？")

        assert not result.was_filtered


class TestAnswerFiltering:
    """Additional tests for answer leak detection."""

    @pytest.mark.unit
    def test_filters_x_equals_number(self) -> None:
        """x = N pattern should be filtered."""
        processor = HintPostProcessor()

        result = processor.process("答案是 x = 5")

        assert result.was_filtered
        assert result.filter_reason == "answer_leak"

    @pytest.mark.unit
    def test_filters_chinese_equals(self) -> None:
        """Chinese '等于' pattern should be filtered."""
        processor = HintPostProcessor()

        result = processor.process("所以x等于3")

        assert result.was_filtered
        assert result.filter_reason == "answer_leak"

    @pytest.mark.unit
    def test_filters_direct_answer_mention(self) -> None:
        """Direct answer mention should be filtered."""
        processor = HintPostProcessor()

        result = processor.process("答案是：7", problem_answer="7")

        assert result.was_filtered

    @pytest.mark.unit
    def test_concept_hint_without_answer_passes(self) -> None:
        """Concept hint that doesn't reveal answer should pass."""
        processor = HintPostProcessor()

        result = processor.process("这是一道一元一次方程，想想等式的性质")

        assert not result.was_filtered

    @pytest.mark.unit
    def test_empty_content_gets_fallback(self) -> None:
        """Empty hint content should get fallback."""
        processor = HintPostProcessor()

        result = processor.process("")

        assert result.was_filtered
        assert result.filter_reason == "empty_content"
        assert len(result.content) > 0


class TestIsValid:
    """Tests for the is_valid helper method."""

    @pytest.mark.unit
    def test_valid_hint_returns_true(self) -> None:
        """Valid hint should return True."""
        processor = HintPostProcessor()

        assert processor.is_valid("想一想，解方程的第一步是什么？")

    @pytest.mark.unit
    def test_invalid_hint_with_answer_returns_false(self) -> None:
        """Hint with answer should return False."""
        processor = HintPostProcessor()

        assert not processor.is_valid("答案是 x = 3")

    @pytest.mark.unit
    def test_invalid_hint_with_negative_returns_false(self) -> None:
        """Hint with negative word should return False."""
        processor = HintPostProcessor()

        assert not processor.is_valid("你做错了")
