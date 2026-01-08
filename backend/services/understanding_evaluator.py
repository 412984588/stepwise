from dataclasses import dataclass, field

from backend.models.enums import ProblemType, HintLayer, UnderstandingLevel


@dataclass
class EvaluationResult:
    understanding_level: UnderstandingLevel
    char_count: int
    keywords_matched: list[str] = field(default_factory=list)


class UnderstandingEvaluator:
    MIN_RESPONSE_LENGTH = 10

    EXPLICIT_CONFUSION_PHRASES = [
        "不懂",
        "不知道",
        "不会",
        "不明白",
        "看不懂",
        "搞不懂",
        "不理解",
        "没听懂",
        "不太懂",
        "看不明白",
    ]

    KEYWORDS_BY_TYPE = {
        ProblemType.LINEAR_EQUATION_1VAR: [
            "移项",
            "等式",
            "方程",
            "未知数",
            "解",
            "x",
            "两边",
            "系数",
            "常数",
            "合并",
            "同类项",
        ],
        ProblemType.QUADRATIC_EQUATION: [
            "因式",
            "分解",
            "配方",
            "求根公式",
            "判别式",
            "二次",
            "根",
            "解",
            "方程",
        ],
        ProblemType.LINEAR_EQUATION_2VAR: [
            "消元",
            "代入",
            "方程组",
            "未知数",
            "解",
        ],
        ProblemType.GEOMETRY_BASIC: [
            "面积",
            "周长",
            "公式",
            "角",
            "边",
            "直角",
            "三角形",
            "圆",
            "正方形",
            "矩形",
        ],
        ProblemType.ARITHMETIC: [
            "加",
            "减",
            "乘",
            "除",
            "运算",
            "顺序",
            "括号",
        ],
        ProblemType.UNKNOWN: [
            "方法",
            "步骤",
            "思路",
            "解决",
        ],
    }

    def evaluate(
        self,
        response_text: str,
        problem_type: ProblemType,
        layer: HintLayer,
    ) -> EvaluationResult:
        text = response_text.strip()
        char_count = len(text)

        if self._contains_explicit_confusion(text):
            return EvaluationResult(
                understanding_level=UnderstandingLevel.EXPLICIT_CONFUSED,
                char_count=char_count,
                keywords_matched=[],
            )

        if char_count < self.MIN_RESPONSE_LENGTH:
            return EvaluationResult(
                understanding_level=UnderstandingLevel.CONFUSED,
                char_count=char_count,
                keywords_matched=[],
            )

        keywords_matched = self._find_matching_keywords(text, problem_type)

        if keywords_matched:
            return EvaluationResult(
                understanding_level=UnderstandingLevel.UNDERSTOOD,
                char_count=char_count,
                keywords_matched=keywords_matched,
            )

        return EvaluationResult(
            understanding_level=UnderstandingLevel.CONFUSED,
            char_count=char_count,
            keywords_matched=[],
        )

    def _contains_explicit_confusion(self, text: str) -> bool:
        text_lower = text.lower()
        for phrase in self.EXPLICIT_CONFUSION_PHRASES:
            if phrase in text_lower:
                return True
        return False

    def _find_matching_keywords(self, text: str, problem_type: ProblemType) -> list[str]:
        keywords = self.KEYWORDS_BY_TYPE.get(problem_type, [])
        keywords.extend(self.KEYWORDS_BY_TYPE.get(ProblemType.UNKNOWN, []))

        matched = []
        text_lower = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                matched.append(keyword)

        return list(set(matched))
