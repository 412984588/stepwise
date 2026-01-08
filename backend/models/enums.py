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

    UNDERSTOOD = "understood"  # ≥10 chars + ≥1 keyword → advance layer
    CONFUSED = "confused"  # <10 chars or no keywords → more guidance
    EXPLICIT_CONFUSED = "explicit_confused"  # Contains "don't understand" etc → more guidance


class MathTopic(str, Enum):
    """US K-12 math curriculum topics aligned with Common Core standards.

    Organized by major domains for grades 4-9.
    """

    # Number & Operations (Grades 4-6)
    WHOLE_NUMBERS = "whole_numbers"  # Multi-digit operations
    FRACTIONS = "fractions"  # Fraction operations
    DECIMALS = "decimals"  # Decimal operations
    PERCENTS = "percents"  # Percent problems
    RATIOS = "ratios"  # Ratio and proportion

    # Pre-Algebra (Grades 6-7)
    INTEGERS = "integers"  # Positive/negative numbers
    ORDER_OF_OPERATIONS = "order_of_operations"  # PEMDAS
    EXPRESSIONS = "expressions"  # Algebraic expressions
    ONE_STEP_EQUATIONS = "one_step_equations"  # x + 5 = 10
    TWO_STEP_EQUATIONS = "two_step_equations"  # 2x + 3 = 11

    # Algebra (Grades 7-9)
    LINEAR_EQUATIONS = "linear_equations"  # Multi-step linear equations
    SYSTEMS_OF_EQUATIONS = "systems_of_equations"  # Two-variable systems
    QUADRATIC_EQUATIONS = "quadratic_equations"  # ax² + bx + c = 0
    INEQUALITIES = "inequalities"  # Linear inequalities

    # Geometry (Grades 4-9)
    AREA_PERIMETER = "area_perimeter"  # 2D measurements
    VOLUME_SURFACE_AREA = "volume_surface_area"  # 3D measurements
    ANGLES = "angles"  # Angle relationships
    TRIANGLES = "triangles"  # Triangle properties
    COORDINATE_GEOMETRY = "coordinate_geometry"  # Graphing, slope

    # Statistics & Probability (Grades 6-9)
    MEAN_MEDIAN_MODE = "mean_median_mode"  # Measures of center
    PROBABILITY = "probability"  # Basic probability

    # Catch-all
    UNKNOWN = "unknown"


class GradeLevel(int, Enum):
    """US grade levels supported (4th through 9th grade)."""

    GRADE_4 = 4
    GRADE_5 = 5
    GRADE_6 = 6
    GRADE_7 = 7
    GRADE_8 = 8
    GRADE_9 = 9


class SubscriptionTier(str, Enum):
    """Subscription tiers for billing.

    FREE: 3 problems/day, basic hints
    PRO: Unlimited problems, all features
    FAMILY: Pro features + up to 5 student profiles
    """

    FREE = "free"
    PRO = "pro"
    FAMILY = "family"


class SubscriptionStatus(str, Enum):
    """Status of a Stripe subscription."""

    ACTIVE = "active"  # Subscription is active and paid
    CANCELED = "canceled"  # User canceled, access until period end
    PAST_DUE = "past_due"  # Payment failed, grace period
    UNPAID = "unpaid"  # Payment failed, access revoked
    TRIALING = "trialing"  # In trial period
