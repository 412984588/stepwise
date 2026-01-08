"""Enumeration types for StepWise models."""

from enum import Enum


class ProblemType(str, Enum):
    """Types of math problems the system can handle.

    Used for problem classification and hint template selection.
    """

    LINEAR_EQUATION_1VAR = "linear_equation_1var"  # 一元一次方程: 3x + 5 = 14
    LINEAR_EQUATION_2VAR = "linear_equation_2var"  # 二元一次方程组: x + y = 5, 2x - y = 1
    QUADRATIC_EQUATION = "quadratic_equation"  # 一元二次方程: x² + 2x - 3 = 0
    GEOMETRY_BASIC = "geometry_basic"  # 基础几何: 三角形面积计算
    ARITHMETIC = "arithmetic"  # 四则运算: 23 × 17 + 45
    UNKNOWN = "unknown"  # 未识别


class Difficulty(str, Enum):
    """Problem difficulty levels."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class HintLayer(str, Enum):
    """Layers in the Socratic hint progression.

    Students progress through layers as they demonstrate understanding.
    """

    CONCEPT = "concept"  # 概念提示层 - 引导回忆相关概念
    STRATEGY = "strategy"  # 策略提示层 - 引导思考解题方向
    STEP = "step"  # 步骤提示层 - 引导执行具体步骤
    COMPLETED = "completed"  # 学生已独立完成
    REVEALED = "revealed"  # 已展示完整解答


class SessionStatus(str, Enum):
    """Status of a hint session."""

    ACTIVE = "active"  # 进行中
    PAUSED = "paused"  # 暂停（学生离开）
    COMPLETED = "completed"  # 正常完成（学生独立解决）
    REVEALED = "revealed"  # 使用完整解答后结束
    ABANDONED = "abandoned"  # 放弃（超时未活动）


class UnderstandingLevel(str, Enum):
    """System's assessment of student understanding.

    Determines whether student advances to next layer or gets more guidance.
    """

    UNDERSTOOD = "understood"  # ≥10字符 且 ≥1关键词 → 进入下一层
    CONFUSED = "confused"  # <10字符 或 无关键词 → 补充引导
    EXPLICIT_CONFUSED = "explicit_confused"  # 包含"不懂"、"不知道"等 → 补充引导
