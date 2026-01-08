import pytest
from unittest.mock import MagicMock

from backend.models.enums import ProblemType
from backend.services.problem_classifier import ProblemClassifier


class TestClassifyLinearEquation:
    @pytest.mark.unit
    def test_classify_simple_linear_equation(self, mock_llm_client: MagicMock) -> None:
        """3x + 5 = 14 should be classified as LINEAR_EQUATION_1VAR."""
        mock_llm_client.classify.return_value = "linear_equation_1var"
        classifier = ProblemClassifier(llm_client=mock_llm_client)

        result = classifier.classify("3x + 5 = 14")

        assert result == ProblemType.LINEAR_EQUATION_1VAR

    @pytest.mark.unit
    def test_classify_linear_equation_with_subtraction(self, mock_llm_client: MagicMock) -> None:
        """2x - 7 = 15 should be classified as LINEAR_EQUATION_1VAR."""
        mock_llm_client.classify.return_value = "linear_equation_1var"
        classifier = ProblemClassifier(llm_client=mock_llm_client)

        result = classifier.classify("2x - 7 = 15")

        assert result == ProblemType.LINEAR_EQUATION_1VAR

    @pytest.mark.unit
    def test_classify_linear_equation_natural_language(self, mock_llm_client: MagicMock) -> None:
        """Natural language description should also be classified correctly."""
        mock_llm_client.classify.return_value = "linear_equation_1var"
        classifier = ProblemClassifier(llm_client=mock_llm_client)

        result = classifier.classify("解方程：3x加5等于14")

        assert result == ProblemType.LINEAR_EQUATION_1VAR

    @pytest.mark.unit
    def test_fallback_when_llm_fails(self, mock_llm_client: MagicMock) -> None:
        """Rule-based fallback should work when LLM returns invalid result."""
        mock_llm_client.classify.return_value = "invalid_type"
        classifier = ProblemClassifier(llm_client=mock_llm_client)

        result = classifier.classify("3x + 5 = 14")

        assert result == ProblemType.LINEAR_EQUATION_1VAR

    @pytest.mark.unit
    def test_fallback_without_llm(self) -> None:
        """Rule-based classification should work without LLM."""
        classifier = ProblemClassifier(llm_client=None)

        result = classifier.classify("3x + 5 = 14")

        assert result == ProblemType.LINEAR_EQUATION_1VAR


class TestClassifyOtherTypes:
    @pytest.mark.unit
    def test_classify_quadratic_equation(self, mock_llm_client: MagicMock) -> None:
        """x² + 2x - 3 = 0 should be classified as QUADRATIC_EQUATION."""
        mock_llm_client.classify.return_value = "quadratic_equation"
        classifier = ProblemClassifier(llm_client=mock_llm_client)

        result = classifier.classify("x² + 2x - 3 = 0")

        assert result == ProblemType.QUADRATIC_EQUATION

    @pytest.mark.unit
    def test_classify_two_variable_linear(self, mock_llm_client: MagicMock) -> None:
        """System of equations should be classified as LINEAR_EQUATION_2VAR."""
        mock_llm_client.classify.return_value = "linear_equation_2var"
        classifier = ProblemClassifier(llm_client=mock_llm_client)

        result = classifier.classify("x + y = 5, 2x - y = 1")

        assert result == ProblemType.LINEAR_EQUATION_2VAR

    @pytest.mark.unit
    def test_classify_unknown_problem(self, mock_llm_client: MagicMock) -> None:
        """Unrecognizable input should return UNKNOWN."""
        mock_llm_client.classify.return_value = "unknown"
        classifier = ProblemClassifier(llm_client=None)

        result = classifier.classify("今天天气真好")

        assert result == ProblemType.UNKNOWN
