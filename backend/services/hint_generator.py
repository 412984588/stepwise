from dataclasses import dataclass
from typing import Protocol

from backend.models.enums import ProblemType, HintLayer
from backend.services.hint_postprocessor import HintPostProcessor


class LLMClientProtocol(Protocol):
    def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str: ...


@dataclass
class GeneratedHint:
    content: str
    layer: HintLayer
    sequence: int = 1
    is_downgrade: bool = False


class HintGenerator:
    LAYER_PROMPTS = {
        HintLayer.CONCEPT: (
            "你是一个苏格拉底式的数学老师。学生正在解决一道{problem_type}的题目。\n"
            "请给出概念层提示，帮助学生回忆相关的数学概念，但绝对不要给出答案或具体步骤。\n"
            "使用鼓励性的语言，不要使用'错'、'不对'等负面词汇。\n"
            "题目: {problem_text}\n"
            "请用中文回答，限制在100字以内。"
        ),
        HintLayer.STRATEGY: (
            "你是一个苏格拉底式的数学老师。学生已经理解了概念，现在需要策略提示。\n"
            "请引导学生思考解题的方向和方法，但不要给出具体的计算步骤或答案。\n"
            "使用鼓励性的语言。\n"
            "题目: {problem_text}\n"
            "请用中文回答，限制在100字以内。"
        ),
        HintLayer.STEP: (
            "你是一个苏格拉底式的数学老师。学生已经知道解题策略，现在需要具体步骤的引导。\n"
            "请引导学生执行第一个具体步骤，但仍然不要直接给出最终答案。\n"
            "使用鼓励性的语言。\n"
            "题目: {problem_text}\n"
            "请用中文回答，限制在100字以内。"
        ),
    }

    FALLBACK_HINTS = {
        HintLayer.CONCEPT: {
            ProblemType.LINEAR_EQUATION_1VAR: "这是一道一元一次方程。你还记得什么是等式的基本性质吗？想一想，我们可以对等式的两边做什么操作而保持等式成立？",
            ProblemType.QUADRATIC_EQUATION: "这是一道一元二次方程。你知道有哪些方法可以解二次方程吗？比如因式分解、配方法或求根公式？",
            ProblemType.LINEAR_EQUATION_2VAR: "这是一道二元一次方程组。想想看，我们怎样才能消去其中一个未知数呢？",
            ProblemType.GEOMETRY_BASIC: "这是一道几何题。让我们先回顾一下相关的几何公式和定理。",
            ProblemType.ARITHMETIC: "这是一道计算题。让我们仔细看看运算的顺序。",
            ProblemType.UNKNOWN: "让我们一起分析这道题目。首先，你能告诉我这道题在问什么吗？",
        },
        HintLayer.STRATEGY: {
            ProblemType.LINEAR_EQUATION_1VAR: "很好！现在想想，为了求出x的值，我们应该怎样处理等式？把含x的项放在一边，常数放在另一边？",
        },
        HintLayer.STEP: {
            ProblemType.LINEAR_EQUATION_1VAR: "现在，让我们执行第一步。看看等式左边，有什么可以移到右边的吗？",
        },
    }

    def __init__(self, llm_client: LLMClientProtocol | None = None) -> None:
        self._llm_client = llm_client
        self._postprocessor = HintPostProcessor()

    def generate(
        self,
        problem_text: str,
        problem_type: ProblemType,
        layer: HintLayer,
        sequence: int = 1,
        is_downgrade: bool = False,
    ) -> GeneratedHint:
        content = self._generate_content(problem_text, problem_type, layer)

        processed = self._postprocessor.process(content)
        if processed.was_filtered and processed.filter_reason in (
            "answer_leak",
            "direct_answer_leak",
        ):
            content = self._get_fallback(problem_type, layer)
        else:
            content = processed.content

        return GeneratedHint(
            content=content,
            layer=layer,
            sequence=sequence,
            is_downgrade=is_downgrade,
        )

    def _generate_content(
        self, problem_text: str, problem_type: ProblemType, layer: HintLayer
    ) -> str:
        if self._llm_client and layer in self.LAYER_PROMPTS:
            try:
                prompt = self.LAYER_PROMPTS[layer].format(
                    problem_type=self._get_problem_type_display(problem_type),
                    problem_text=problem_text,
                )
                return self._llm_client.complete(
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=200,
                )
            except Exception:
                pass

        return self._get_fallback(problem_type, layer)

    def _get_fallback(self, problem_type: ProblemType, layer: HintLayer) -> str:
        layer_fallbacks = self.FALLBACK_HINTS.get(layer, {})
        if problem_type in layer_fallbacks:
            return layer_fallbacks[problem_type]

        concept_fallbacks = self.FALLBACK_HINTS.get(HintLayer.CONCEPT, {})
        return concept_fallbacks.get(problem_type, concept_fallbacks[ProblemType.UNKNOWN])

    def _get_problem_type_display(self, problem_type: ProblemType) -> str:
        display_names = {
            ProblemType.LINEAR_EQUATION_1VAR: "一元一次方程",
            ProblemType.LINEAR_EQUATION_2VAR: "二元一次方程组",
            ProblemType.QUADRATIC_EQUATION: "一元二次方程",
            ProblemType.GEOMETRY_BASIC: "基础几何",
            ProblemType.ARITHMETIC: "四则运算",
            ProblemType.UNKNOWN: "数学问题",
        }
        return display_names.get(problem_type, "数学问题")
