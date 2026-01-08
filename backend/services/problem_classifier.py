"""Problem classifier service for StepWise.

Classifies math problems into ProblemType categories using LLM with rule-based fallback.
"""

import re
from typing import Any

from backend.models.enums import ProblemType


class ProblemClassifier:
    """Classifies math problems into problem types.

    Uses LLM classification when available, falls back to rule-based patterns.
    """

    def __init__(self, llm_client: Any | None = None) -> None:
        """Initialize classifier.

        Args:
            llm_client: Optional LLM client with classify() method.
                       If None, uses rule-based classification only.
        """
        self._llm_client = llm_client

    def classify(self, problem_text: str) -> ProblemType:
        """Classify a math problem into a problem type.

        Args:
            problem_text: The problem text to classify.

        Returns:
            The classified ProblemType.
        """
        # 尝试 LLM 分类
        if self._llm_client is not None:
            try:
                llm_result = self._llm_client.classify(problem_text)
                problem_type = self._parse_llm_result(llm_result)
                if problem_type != ProblemType.UNKNOWN:
                    return problem_type
            except Exception:
                pass  # fallback 到规则分类

        # 规则 fallback
        return self._classify_by_rules(problem_text)

    def _parse_llm_result(self, result: str) -> ProblemType:
        """Parse LLM result string to ProblemType.

        Args:
            result: The LLM classification result string.

        Returns:
            Corresponding ProblemType or UNKNOWN if invalid.
        """
        result_lower = result.lower().strip()

        for problem_type in ProblemType:
            if problem_type.value == result_lower:
                return problem_type

        return ProblemType.UNKNOWN

    def _classify_by_rules(self, problem_text: str) -> ProblemType:
        """Classify using rule-based pattern matching.

        Args:
            problem_text: The problem text to classify.

        Returns:
            Classified ProblemType based on patterns.
        """
        text = problem_text.lower()

        # 检测二元方程组 (有逗号分隔的两个方程，含 x 和 y)
        if (',' in text or '，' in text) and 'x' in text and 'y' in text:
            return ProblemType.LINEAR_EQUATION_2VAR

        # 检测一元二次方程 (含 x² 或 x^2)
        if 'x²' in text or 'x^2' in text or 'x2' in text:
            return ProblemType.QUADRATIC_EQUATION

        # 检测一元一次方程 (含 x 和 =)
        if 'x' in text and '=' in text:
            return ProblemType.LINEAR_EQUATION_1VAR

        # 检测中文一元一次方程描述
        if ('解方程' in text or '求解' in text) and 'x' in text:
            return ProblemType.LINEAR_EQUATION_1VAR

        return ProblemType.UNKNOWN
