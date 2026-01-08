import pytest
from unittest.mock import MagicMock

from backend.models.enums import ProblemType, HintLayer
from backend.services.hint_generator import HintGenerator


class TestConceptHintNoAnswer:
    @pytest.mark.unit
    def test_concept_hint_does_not_contain_numeric_answer(self, mock_llm_client: MagicMock) -> None:
        """Concept hint for '3x + 5 = 14' must NOT contain 'x = 3' or '= 3'."""
        mock_llm_client.complete.return_value = (
            "这道题是一元一次方程。想一想，什么是方程的解？"
            "我们需要找到一个数，代入x后能使等式成立。"
        )
        generator = HintGenerator(llm_client=mock_llm_client)

        hint = generator.generate(
            problem_text="3x + 5 = 14",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert "x = 3" not in hint.content
        assert "x=3" not in hint.content
        assert "= 3" not in hint.content
        assert "等于3" not in hint.content

    @pytest.mark.unit
    def test_concept_hint_does_not_reveal_steps(self, mock_llm_client: MagicMock) -> None:
        """Concept hint must NOT reveal solution steps like '移项' with specific values."""
        mock_llm_client.complete.return_value = "解方程的关键是把未知数和常数分开。你知道怎样做吗？"
        generator = HintGenerator(llm_client=mock_llm_client)

        hint = generator.generate(
            problem_text="3x + 5 = 14",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert "3x = 9" not in hint.content
        assert "3x=9" not in hint.content
        assert "14 - 5" not in hint.content

    @pytest.mark.unit
    def test_concept_hint_returns_correct_layer(self, mock_llm_client: MagicMock) -> None:
        """Generated hint should have CONCEPT layer."""
        mock_llm_client.complete.return_value = "这是一道关于方程的题目。"
        generator = HintGenerator(llm_client=mock_llm_client)

        hint = generator.generate(
            problem_text="3x + 5 = 14",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert hint.layer == HintLayer.CONCEPT

    @pytest.mark.unit
    def test_concept_hint_is_not_empty(self, mock_llm_client: MagicMock) -> None:
        """Generated hint must have content."""
        mock_llm_client.complete.return_value = "让我们先回顾一下一元一次方程的概念。"
        generator = HintGenerator(llm_client=mock_llm_client)

        hint = generator.generate(
            problem_text="3x + 5 = 14",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert len(hint.content) > 0

    @pytest.mark.unit
    def test_llm_answer_leak_is_filtered(self, mock_llm_client: MagicMock) -> None:
        """If LLM accidentally includes answer, post-processor should filter it."""
        mock_llm_client.complete.return_value = "这道题的答案是x = 3。哦不对，让我引导你思考..."
        generator = HintGenerator(llm_client=mock_llm_client)

        hint = generator.generate(
            problem_text="3x + 5 = 14",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.CONCEPT,
        )

        assert "x = 3" not in hint.content
        assert "x=3" not in hint.content


class TestHintGeneratorLayers:
    @pytest.mark.unit
    def test_strategy_hint_guides_approach(self, mock_llm_client: MagicMock) -> None:
        """Strategy layer should guide solving approach without giving answer."""
        mock_llm_client.complete.return_value = (
            "解一元一次方程的一般步骤是：先移项，再合并同类项，最后求解。"
            "你能试着把含x的项移到等式一边吗？"
        )
        generator = HintGenerator(llm_client=mock_llm_client)

        hint = generator.generate(
            problem_text="3x + 5 = 14",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.STRATEGY,
        )

        assert hint.layer == HintLayer.STRATEGY
        assert "x = 3" not in hint.content

    @pytest.mark.unit
    def test_step_hint_guides_execution(self, mock_llm_client: MagicMock) -> None:
        """Step layer provides more specific guidance without full solution."""
        mock_llm_client.complete.return_value = "很好！现在等式两边都减去5，看看会发生什么？"
        generator = HintGenerator(llm_client=mock_llm_client)

        hint = generator.generate(
            problem_text="3x + 5 = 14",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            layer=HintLayer.STEP,
        )

        assert hint.layer == HintLayer.STEP
        assert "x = 3" not in hint.content
