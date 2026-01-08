import re
from dataclasses import dataclass


@dataclass
class PostProcessResult:
    content: str
    was_filtered: bool
    filter_reason: str | None = None


class HintPostProcessor:
    ANSWER_PATTERNS = [
        r"[xyzXYZ]\s*=\s*-?\d+",
        r"等于\s*-?\d+",
        r"答案[是为：:]\s*-?\d+",
        r"结果[是为：:]\s*-?\d+",
    ]

    STEP_REVEAL_PATTERNS = [
        r"\d+[xyzXYZ]\s*=\s*-?\d+",
        r"\d+\s*[+\-×÷*/]\s*\d+\s*=\s*-?\d+",
    ]

    NEGATIVE_WORDS = [
        "错",
        "不对",
        "错误",
        "wrong",
        "incorrect",
        "mistake",
        "笨",
        "傻",
        "蠢",
    ]

    def process(self, hint_content: str, problem_answer: str | None = None) -> PostProcessResult:
        if not hint_content.strip():
            return PostProcessResult(
                content="让我们一起来思考这道题。",
                was_filtered=True,
                filter_reason="empty_content",
            )

        for pattern in self.ANSWER_PATTERNS:
            if re.search(pattern, hint_content):
                filtered = re.sub(pattern, "[...]", hint_content)
                return PostProcessResult(
                    content=filtered,
                    was_filtered=True,
                    filter_reason="answer_leak",
                )

        if problem_answer:
            if problem_answer in hint_content:
                filtered = hint_content.replace(problem_answer, "[...]")
                return PostProcessResult(
                    content=filtered,
                    was_filtered=True,
                    filter_reason="direct_answer_leak",
                )

        for word in self.NEGATIVE_WORDS:
            if word in hint_content.lower():
                return PostProcessResult(
                    content=hint_content,
                    was_filtered=True,
                    filter_reason="negative_word",
                )

        return PostProcessResult(content=hint_content, was_filtered=False)

    def is_valid(self, hint_content: str) -> bool:
        result = self.process(hint_content)
        return not result.was_filtered
