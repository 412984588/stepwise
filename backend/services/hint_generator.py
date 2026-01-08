from dataclasses import dataclass
from typing import Protocol

from backend.models.enums import ProblemType, HintLayer
from backend.services.hint_postprocessor import HintPostProcessor
from backend.i18n import Locale


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
    LAYER_PROMPTS_EN = {
        HintLayer.CONCEPT: (
            "You are a Socratic math tutor helping a {grade_level} student with a {problem_type} problem.\n"
            "Give a concept-level hint to help them recall relevant math concepts. "
            "Do NOT give the answer or specific steps.\n"
            "Use encouraging language appropriate for their grade level.\n"
            "Problem: {problem_text}\n"
            "Keep your response under 80 words."
        ),
        HintLayer.STRATEGY: (
            "You are a Socratic math tutor. The student understands the concept and needs strategy guidance.\n"
            "Guide them to think about the approach and method, but don't give specific calculation steps or the answer.\n"
            "Use encouraging language for a {grade_level} student.\n"
            "Problem: {problem_text}\n"
            "Keep your response under 80 words."
        ),
        HintLayer.STEP: (
            "You are a Socratic math tutor. The student knows the strategy and needs step-by-step guidance.\n"
            "Guide them to execute the first specific step, but still don't give the final answer.\n"
            "Use encouraging language for a {grade_level} student.\n"
            "Problem: {problem_text}\n"
            "Keep your response under 80 words."
        ),
    }

    LAYER_PROMPTS_ZH = {
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

    FALLBACK_HINTS_EN = {
        HintLayer.CONCEPT: {
            ProblemType.LINEAR_EQUATION_1VAR: "This is a linear equation with one variable. Do you remember the basic properties of equations? Think about what operations you can do to both sides while keeping the equation balanced.",
            ProblemType.QUADRATIC_EQUATION: "This is a quadratic equation. What methods do you know for solving quadratic equations? Think about factoring, completing the square, or the quadratic formula.",
            ProblemType.LINEAR_EQUATION_2VAR: "This is a system of linear equations. How might we eliminate one of the variables?",
            ProblemType.GEOMETRY_BASIC: "This is a geometry problem. Let's start by reviewing the relevant formulas and properties.",
            ProblemType.ARITHMETIC: "This is an arithmetic problem. Let's look carefully at the order of operations.",
            ProblemType.UNKNOWN: "Let's analyze this problem together. First, can you tell me what the problem is asking?",
        },
        HintLayer.STRATEGY: {
            ProblemType.LINEAR_EQUATION_1VAR: "Great! Now think about how to solve for x. What if we put all the x terms on one side and the numbers on the other?",
        },
        HintLayer.STEP: {
            ProblemType.LINEAR_EQUATION_1VAR: "Now let's do the first step. Look at the left side of the equation - what can we move to the right side?",
        },
    }

    FALLBACK_HINTS_ZH = {
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

    PROBLEM_TYPE_DISPLAY_EN = {
        ProblemType.LINEAR_EQUATION_1VAR: "linear equation",
        ProblemType.LINEAR_EQUATION_2VAR: "system of linear equations",
        ProblemType.QUADRATIC_EQUATION: "quadratic equation",
        ProblemType.GEOMETRY_BASIC: "geometry",
        ProblemType.ARITHMETIC: "arithmetic",
        ProblemType.UNKNOWN: "math problem",
    }

    PROBLEM_TYPE_DISPLAY_ZH = {
        ProblemType.LINEAR_EQUATION_1VAR: "一元一次方程",
        ProblemType.LINEAR_EQUATION_2VAR: "二元一次方程组",
        ProblemType.QUADRATIC_EQUATION: "一元二次方程",
        ProblemType.GEOMETRY_BASIC: "基础几何",
        ProblemType.ARITHMETIC: "四则运算",
        ProblemType.UNKNOWN: "数学问题",
    }

    GRADE_DISPLAY = {
        4: "4th grade",
        5: "5th grade",
        6: "6th grade",
        7: "7th grade",
        8: "8th grade",
        9: "9th grade",
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
        locale: str = "en-US",
        grade_level: int | None = None,
    ) -> GeneratedHint:
        content = self._generate_content(problem_text, problem_type, layer, locale, grade_level)

        processed = self._postprocessor.process(content)
        if processed.was_filtered and processed.filter_reason in (
            "answer_leak",
            "direct_answer_leak",
        ):
            content = self._get_fallback(problem_type, layer, locale)
        else:
            content = processed.content

        return GeneratedHint(
            content=content,
            layer=layer,
            sequence=sequence,
            is_downgrade=is_downgrade,
        )

    def _generate_content(
        self,
        problem_text: str,
        problem_type: ProblemType,
        layer: HintLayer,
        locale: str,
        grade_level: int | None,
    ) -> str:
        is_english = locale.startswith("en")
        prompts = self.LAYER_PROMPTS_EN if is_english else self.LAYER_PROMPTS_ZH

        if self._llm_client and layer in prompts:
            try:
                prompt = prompts[layer].format(
                    problem_type=self._get_problem_type_display(problem_type, locale),
                    problem_text=problem_text,
                    grade_level=self._get_grade_display(grade_level),
                )
                return self._llm_client.complete(
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=200,
                )
            except Exception:
                pass

        return self._get_fallback(problem_type, layer, locale)

    def _get_fallback(self, problem_type: ProblemType, layer: HintLayer, locale: str) -> str:
        is_english = locale.startswith("en")
        fallbacks = self.FALLBACK_HINTS_EN if is_english else self.FALLBACK_HINTS_ZH

        layer_fallbacks = fallbacks.get(layer, {})
        if problem_type in layer_fallbacks:
            return layer_fallbacks[problem_type]

        concept_fallbacks = fallbacks.get(HintLayer.CONCEPT, {})
        return concept_fallbacks.get(problem_type, concept_fallbacks[ProblemType.UNKNOWN])

    def _get_problem_type_display(self, problem_type: ProblemType, locale: str) -> str:
        is_english = locale.startswith("en")
        display_names = self.PROBLEM_TYPE_DISPLAY_EN if is_english else self.PROBLEM_TYPE_DISPLAY_ZH
        default = "math problem" if is_english else "数学问题"
        return display_names.get(problem_type, default)

    def _get_grade_display(self, grade_level: int | None) -> str:
        if grade_level is None:
            return "middle school"
        return self.GRADE_DISPLAY.get(grade_level, f"grade {grade_level}")
