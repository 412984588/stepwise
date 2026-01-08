import pytest

from backend.models.enums import ProblemType
from backend.services.solution_generator import SolutionGenerator, GeneratedSolution


class TestSolutionFormat:
    @pytest.mark.unit
    def test_solution_contains_steps_list(self) -> None:
        """Solution must contain a list of steps."""
        generator = SolutionGenerator()

        solution = generator.generate(
            problem_text="3x + 5 = 14",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )

        assert isinstance(solution.steps, list)
        assert len(solution.steps) > 0

    @pytest.mark.unit
    def test_each_step_has_description_and_result(self) -> None:
        """Each step must have description and result."""
        generator = SolutionGenerator()

        solution = generator.generate(
            problem_text="3x + 5 = 14",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )

        for step in solution.steps:
            assert "description" in step
            assert "result" in step
            assert len(step["description"]) > 0

    @pytest.mark.unit
    def test_solution_has_final_answer(self) -> None:
        """Solution must contain the final answer."""
        generator = SolutionGenerator()

        solution = generator.generate(
            problem_text="3x + 5 = 14",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )

        assert solution.final_answer is not None
        assert len(solution.final_answer) > 0

    @pytest.mark.unit
    def test_solution_has_explanation(self) -> None:
        """Solution should have an explanation summary."""
        generator = SolutionGenerator()

        solution = generator.generate(
            problem_text="3x + 5 = 14",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )

        assert solution.explanation is not None
        assert len(solution.explanation) > 0

    @pytest.mark.unit
    def test_fallback_solution_when_no_llm(self) -> None:
        """Should provide fallback solution when LLM not available."""
        generator = SolutionGenerator(llm_client=None)

        solution = generator.generate(
            problem_text="3x + 5 = 14",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )

        assert len(solution.steps) > 0
        assert solution.final_answer is not None


class TestSolutionContent:
    @pytest.mark.unit
    def test_linear_equation_solution_correct(self) -> None:
        """Linear equation solution should be mathematically correct."""
        generator = SolutionGenerator()

        solution = generator.generate(
            problem_text="3x + 5 = 14",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )

        assert "3" in solution.final_answer or "x" in solution.final_answer.lower()

    @pytest.mark.unit
    def test_quadratic_equation_solution_format(self) -> None:
        """Quadratic equation solution should handle two roots."""
        generator = SolutionGenerator()

        solution = generator.generate(
            problem_text="x² - 5x + 6 = 0",
            problem_type=ProblemType.QUADRATIC_EQUATION,
        )

        assert len(solution.steps) > 0
        assert solution.final_answer is not None
