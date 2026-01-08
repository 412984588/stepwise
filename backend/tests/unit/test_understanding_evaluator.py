import pytest

from backend.models.enums import ProblemType, HintLayer, UnderstandingLevel
from backend.services.understanding_evaluator import UnderstandingEvaluator


class TestResponseTooShort:
    @pytest.mark.unit
    def test_response_under_10_chars_is_confused(self) -> None:
        """Response with fewer than 10 characters should be CONFUSED."""
        evaluator = UnderstandingEvaluator()

        result = evaluator.evaluate(
            response_text="嗯好的",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert result.understanding_level == UnderstandingLevel.CONFUSED
        assert result.char_count < 10

    @pytest.mark.unit
    def test_response_exactly_10_chars_with_keyword_is_understood(self) -> None:
        """Response with exactly 10 chars and keyword should be UNDERSTOOD."""
        evaluator = UnderstandingEvaluator()

        result = evaluator.evaluate(
            response_text="我觉得移项可以帮助我们",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert result.char_count >= 10
        if result.keywords_matched:
            assert result.understanding_level == UnderstandingLevel.UNDERSTOOD

    @pytest.mark.unit
    def test_response_10_chars_no_keyword_is_confused(self) -> None:
        """Response with 10+ chars but no keyword should be CONFUSED."""
        evaluator = UnderstandingEvaluator()

        result = evaluator.evaluate(
            response_text="我觉得这道题很有趣啊",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert result.char_count >= 10
        assert result.understanding_level == UnderstandingLevel.CONFUSED

    @pytest.mark.unit
    def test_empty_response_is_confused(self) -> None:
        """Empty response should be CONFUSED."""
        evaluator = UnderstandingEvaluator()

        result = evaluator.evaluate(
            response_text="",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert result.understanding_level == UnderstandingLevel.CONFUSED
        assert result.char_count == 0

    @pytest.mark.unit
    def test_whitespace_only_response_is_confused(self) -> None:
        """Whitespace-only response should be CONFUSED."""
        evaluator = UnderstandingEvaluator()

        result = evaluator.evaluate(
            response_text="     ",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert result.understanding_level == UnderstandingLevel.CONFUSED


class TestExplicitConfusion:
    @pytest.mark.unit
    def test_explicit_dont_know_is_explicit_confused(self) -> None:
        """Response containing '不懂' should be EXPLICIT_CONFUSED."""
        evaluator = UnderstandingEvaluator()

        result = evaluator.evaluate(
            response_text="我不懂这道题要怎么做",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert result.understanding_level == UnderstandingLevel.EXPLICIT_CONFUSED

    @pytest.mark.unit
    def test_explicit_dont_understand_is_explicit_confused(self) -> None:
        """Response containing '不知道' should be EXPLICIT_CONFUSED."""
        evaluator = UnderstandingEvaluator()

        result = evaluator.evaluate(
            response_text="我不知道应该怎么解决",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert result.understanding_level == UnderstandingLevel.EXPLICIT_CONFUSED

    @pytest.mark.unit
    def test_explicit_confused_phrase_is_detected(self) -> None:
        """Response with confusion phrases like '看不明白' should be EXPLICIT_CONFUSED."""
        evaluator = UnderstandingEvaluator()

        result = evaluator.evaluate(
            response_text="这个题目我看不明白是什么意思",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert result.understanding_level == UnderstandingLevel.EXPLICIT_CONFUSED


class TestKeywordMatching:
    @pytest.mark.unit
    def test_linear_equation_keyword_移项_matches(self) -> None:
        """'移项' keyword should match for linear equation."""
        evaluator = UnderstandingEvaluator()

        result = evaluator.evaluate(
            response_text="我觉得应该用移项的方法来解这道题",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert "移项" in result.keywords_matched
        assert result.understanding_level == UnderstandingLevel.UNDERSTOOD

    @pytest.mark.unit
    def test_linear_equation_keyword_等式性质_matches(self) -> None:
        """'等式' keyword should match for linear equation."""
        evaluator = UnderstandingEvaluator()

        result = evaluator.evaluate(
            response_text="根据等式性质，两边同时减去相同的数",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert any("等式" in kw for kw in result.keywords_matched)
        assert result.understanding_level == UnderstandingLevel.UNDERSTOOD

    @pytest.mark.unit
    def test_quadratic_keyword_分解因式_matches(self) -> None:
        """'因式分解' keyword should match for quadratic equation."""
        evaluator = UnderstandingEvaluator()

        result = evaluator.evaluate(
            response_text="这道二次方程可以用因式分解来解决",
            problem_type=ProblemType.QUADRATIC_EQUATION,
            layer=HintLayer.STRATEGY,
        )

        assert any("因式" in kw for kw in result.keywords_matched)
        assert result.understanding_level == UnderstandingLevel.UNDERSTOOD


class TestUnderstandingWithKeywords:
    """T047: Tests for understanding evaluation with keyword matching."""

    @pytest.mark.unit
    def test_understood_when_10_chars_and_keyword(self) -> None:
        """≥10 chars + ≥1 keyword = UNDERSTOOD."""
        evaluator = UnderstandingEvaluator()

        result = evaluator.evaluate(
            response_text="我想用移项的方法来解这道方程",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert result.understanding_level == UnderstandingLevel.UNDERSTOOD
        assert result.char_count >= 10
        assert len(result.keywords_matched) >= 1

    @pytest.mark.unit
    def test_understood_with_multiple_keywords(self) -> None:
        """Multiple keywords should all be captured."""
        evaluator = UnderstandingEvaluator()

        result = evaluator.evaluate(
            response_text="移项后合并同类项，然后求解方程",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.STRATEGY,
        )

        assert result.understanding_level == UnderstandingLevel.UNDERSTOOD
        assert len(result.keywords_matched) >= 2

    @pytest.mark.unit
    def test_understood_progresses_layer(self) -> None:
        """UNDERSTOOD result on CONCEPT should allow STRATEGY progression."""
        evaluator = UnderstandingEvaluator()

        result = evaluator.evaluate(
            response_text="等式性质是指两边同时加减乘除相同的数",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert result.understanding_level == UnderstandingLevel.UNDERSTOOD


class TestConfusionStaysOnLayer:
    """T048: Tests that CONFUSED keeps student on same layer."""

    @pytest.mark.unit
    def test_confused_no_keyword_stays_on_layer(self) -> None:
        """Response without keywords should be CONFUSED, staying on layer."""
        evaluator = UnderstandingEvaluator()

        result = evaluator.evaluate(
            response_text="我觉得这道题目挺有意思的呢",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert result.understanding_level == UnderstandingLevel.CONFUSED
        assert result.char_count >= 10
        assert len(result.keywords_matched) == 0

    @pytest.mark.unit
    def test_confused_short_response_stays_on_layer(self) -> None:
        """Short response should be CONFUSED, staying on layer."""
        evaluator = UnderstandingEvaluator()

        result = evaluator.evaluate(
            response_text="嗯嗯好的",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.STRATEGY,
        )

        assert result.understanding_level == UnderstandingLevel.CONFUSED
        assert result.char_count < 10

    @pytest.mark.unit
    def test_explicit_confused_stays_on_layer(self) -> None:
        """Explicit confusion phrase should stay on layer."""
        evaluator = UnderstandingEvaluator()

        result = evaluator.evaluate(
            response_text="我完全不理解这道题应该怎么处理",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert result.understanding_level == UnderstandingLevel.EXPLICIT_CONFUSED


class TestConfusionDowngrade:
    """T049: Tests for confusion count and downgrade triggering."""

    @pytest.mark.unit
    def test_confusion_count_tracked_per_evaluation(self) -> None:
        """Each confused response should be trackable for counting."""
        evaluator = UnderstandingEvaluator()

        responses = ["不太确定", "还是不懂", "我不明白"]
        confusion_count = 0

        for response in responses:
            result = evaluator.evaluate(
                response_text=response,
                problem_type=ProblemType.LINEAR_EQUATION_1VAR,
                layer=HintLayer.CONCEPT,
            )
            if result.understanding_level in (
                UnderstandingLevel.CONFUSED,
                UnderstandingLevel.EXPLICIT_CONFUSED,
            ):
                confusion_count += 1

        assert confusion_count == 3

    @pytest.mark.unit
    def test_three_confusions_should_trigger_downgrade(self) -> None:
        """After 3 confused responses, system should track downgrade eligibility."""
        evaluator = UnderstandingEvaluator()

        confused_responses = [
            "我不太明白",
            "还是搞不懂",
            "我真的不知道",
        ]

        all_confused = True
        for response in confused_responses:
            result = evaluator.evaluate(
                response_text=response,
                problem_type=ProblemType.LINEAR_EQUATION_1VAR,
                layer=HintLayer.CONCEPT,
            )
            if result.understanding_level == UnderstandingLevel.UNDERSTOOD:
                all_confused = False

        assert all_confused

    @pytest.mark.unit
    def test_understood_resets_confusion_eligibility(self) -> None:
        """UNDERSTOOD response should break confusion streak."""
        evaluator = UnderstandingEvaluator()

        result1 = evaluator.evaluate(
            response_text="不太确定",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )
        assert result1.understanding_level != UnderstandingLevel.UNDERSTOOD

        result2 = evaluator.evaluate(
            response_text="哦我明白了，用移项的方法把常数移到右边",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )
        assert result2.understanding_level == UnderstandingLevel.UNDERSTOOD


class TestEvaluationResult:
    @pytest.mark.unit
    def test_result_contains_char_count(self) -> None:
        """Evaluation result should contain character count."""
        evaluator = UnderstandingEvaluator()

        result = evaluator.evaluate(
            response_text="这是一个测试回复",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert result.char_count == 8

    @pytest.mark.unit
    def test_result_contains_keywords_list(self) -> None:
        """Evaluation result should contain matched keywords list."""
        evaluator = UnderstandingEvaluator()

        result = evaluator.evaluate(
            response_text="移项和合并同类项是解方程的基本步骤",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert isinstance(result.keywords_matched, list)
