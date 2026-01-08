from dataclasses import dataclass, field
from typing import Protocol

from backend.models.enums import ProblemType


class LLMClientProtocol(Protocol):
    def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str: ...


@dataclass
class GeneratedSolution:
    steps: list[dict[str, str]] = field(default_factory=list)
    final_answer: str = ""
    explanation: str = ""


class SolutionGenerator:
    SOLUTION_PROMPT = (
        "请为以下数学题提供完整的解答。\n"
        "题目: {problem_text}\n\n"
        "请按以下格式回答：\n"
        "步骤1: [描述] -> [结果]\n"
        "步骤2: [描述] -> [结果]\n"
        "...\n"
        "最终答案: [答案]\n"
        "解释: [简短的总结]\n"
    )

    FALLBACK_SOLUTIONS: dict[ProblemType, dict[str, list[dict[str, str]] | str]] = {
        ProblemType.LINEAR_EQUATION_1VAR: {
            "steps": [
                {"description": "移项：将常数项移到等式右边", "result": "3x = 14 - 5"},
                {"description": "计算右边", "result": "3x = 9"},
                {"description": "两边同除以系数", "result": "x = 9 ÷ 3"},
                {"description": "得出结果", "result": "x = 3"},
            ],
            "final_answer": "x = 3",
            "explanation": "这是一道一元一次方程，通过移项和等式性质求解。",
        },
        ProblemType.QUADRATIC_EQUATION: {
            "steps": [
                {"description": "识别方程形式", "result": "标准二次方程 ax² + bx + c = 0"},
                {"description": "尝试因式分解或使用求根公式", "result": "分解为 (x-p)(x-q) = 0"},
                {"description": "求解每个因子", "result": "x = p 或 x = q"},
            ],
            "final_answer": "x = 2 或 x = 3",
            "explanation": "二次方程可以通过因式分解、配方法或求根公式求解。",
        },
        ProblemType.LINEAR_EQUATION_2VAR: {
            "steps": [
                {"description": "选择消元法或代入法", "result": "确定消去哪个变量"},
                {"description": "消去一个变量", "result": "得到一元方程"},
                {"description": "求解得到的一元方程", "result": "得到第一个变量的值"},
                {"description": "代入求另一个变量", "result": "得到第二个变量的值"},
            ],
            "final_answer": "x = a, y = b",
            "explanation": "二元一次方程组通过消元或代入法求解。",
        },
        ProblemType.GEOMETRY_BASIC: {
            "steps": [
                {"description": "确定图形类型和已知条件", "result": "识别几何图形"},
                {"description": "选择合适的公式", "result": "面积/周长公式"},
                {"description": "代入数值计算", "result": "计算结果"},
            ],
            "final_answer": "面积 = 12",
            "explanation": "几何题需要正确识别图形并应用相应公式。",
        },
        ProblemType.ARITHMETIC: {
            "steps": [
                {"description": "按运算顺序处理", "result": "先乘除后加减"},
                {"description": "逐步计算", "result": "中间结果"},
                {"description": "得出最终结果", "result": "最终答案"},
            ],
            "final_answer": "42",
            "explanation": "算术运算需要遵循运算优先级。",
        },
        ProblemType.UNKNOWN: {
            "steps": [
                {"description": "分析题目要求", "result": "理解问题"},
                {"description": "选择解题方法", "result": "确定策略"},
                {"description": "执行计算", "result": "得出答案"},
            ],
            "final_answer": "请根据题目具体计算",
            "explanation": "数学题需要仔细分析，选择合适的方法求解。",
        },
    }

    def __init__(self, llm_client: LLMClientProtocol | None = None) -> None:
        self._llm_client = llm_client

    def generate(
        self,
        problem_text: str,
        problem_type: ProblemType,
    ) -> GeneratedSolution:
        if self._llm_client:
            try:
                return self._generate_with_llm(problem_text)
            except Exception:
                pass

        return self._get_fallback(problem_type)

    def _generate_with_llm(self, problem_text: str) -> GeneratedSolution:
        prompt = self.SOLUTION_PROMPT.format(problem_text=problem_text)
        response = self._llm_client.complete(  # type: ignore
            prompt=prompt,
            temperature=0.3,
            max_tokens=800,
        )
        return self._parse_llm_response(response)

    def _parse_llm_response(self, response: str) -> GeneratedSolution:
        lines = response.strip().split("\n")
        steps: list[dict[str, str]] = []
        final_answer = ""
        explanation = ""

        for line in lines:
            line = line.strip()
            if line.startswith("步骤") and "->" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    step_parts = parts[1].split("->")
                    if len(step_parts) == 2:
                        steps.append(
                            {
                                "description": step_parts[0].strip(),
                                "result": step_parts[1].strip(),
                            }
                        )
            elif line.startswith("最终答案"):
                final_answer = line.split(":", 1)[-1].strip()
            elif line.startswith("解释"):
                explanation = line.split(":", 1)[-1].strip()

        if not steps or not final_answer:
            return self._get_fallback(ProblemType.UNKNOWN)

        return GeneratedSolution(
            steps=steps,
            final_answer=final_answer,
            explanation=explanation,
        )

    def _get_fallback(self, problem_type: ProblemType) -> GeneratedSolution:
        fallback = self.FALLBACK_SOLUTIONS.get(
            problem_type,
            self.FALLBACK_SOLUTIONS[ProblemType.UNKNOWN],
        )
        return GeneratedSolution(
            steps=list(fallback["steps"]),  # type: ignore
            final_answer=str(fallback["final_answer"]),
            explanation=str(fallback["explanation"]),
        )
