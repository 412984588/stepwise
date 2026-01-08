export enum ProblemType {
  LINEAR_EQUATION_1VAR = 'linear_equation_1var',
  LINEAR_EQUATION_2VAR = 'linear_equation_2var',
  QUADRATIC_EQUATION = 'quadratic_equation',
  GEOMETRY_BASIC = 'geometry_basic',
  ARITHMETIC = 'arithmetic',
  UNKNOWN = 'unknown',
}

export enum Difficulty {
  EASY = 'easy',
  MEDIUM = 'medium',
  HARD = 'hard',
}

export enum HintLayer {
  CONCEPT = 'concept',
  STRATEGY = 'strategy',
  STEP = 'step',
  COMPLETED = 'completed',
  REVEALED = 'revealed',
}

export enum SessionStatus {
  ACTIVE = 'active',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  REVEALED = 'revealed',
  ABANDONED = 'abandoned',
}

export enum UnderstandingLevel {
  UNDERSTOOD = 'understood',
  CONFUSED = 'confused',
  EXPLICIT_CONFUSED = 'explicit_confused',
}
