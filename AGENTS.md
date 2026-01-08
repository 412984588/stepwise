# StepWise Agent Guidelines

## Project Overview

Socratic-style math tutoring system with layered hints (Concept → Strategy → Step).

- **Backend**: Python 3.11 + FastAPI + SQLAlchemy + SQLite
- **Frontend**: TypeScript 5.x + React 18 + Vite

## Build & Test Commands

### Backend (from `backend/`)

```bash
pip install -e ".[dev]"           # Install dependencies
pytest tests/ -v                   # Run all tests
pytest tests/unit/test_hint_generator.py -v                              # Single file
pytest tests/unit/test_hint_generator.py::TestConceptHintNoAnswer -v     # Single class
pytest tests/unit/test_hint_generator.py::TestConceptHintNoAnswer::test_concept_hint_does_not_contain_numeric_answer -v  # Single test
pytest -m unit -v                  # By marker (unit/contract)
pytest --cov=. --cov-report=term-missing  # With coverage
ruff check . && black --check . && mypy .  # Lint
black . && ruff check --fix .      # Format
uvicorn backend.main:app --reload  # Dev server
```

### Frontend (from `frontend/`)

```bash
npm install                        # Install dependencies
npm run build                      # Type check + build
npm run lint                       # Lint
npx playwright test                # E2E tests (needs backend running)
npx playwright test tests/e2e/hint-flow.spec.ts  # Single test file
npm run dev                        # Dev server
```

## Code Style - Python

**Imports**: stdlib → third-party → local, separated by blank lines

```python
import re
from dataclasses import dataclass

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from backend.models import Problem, HintSession
from backend.services.hint_generator import HintGenerator
```

**Type Hints**: Required on all functions (mypy strict)

```python
def generate_session_id() -> str:
    return f"ses_{uuid.uuid4().hex[:8]}"
```

**Naming**: Classes=`PascalCase`, functions=`snake_case`, constants=`UPPER_SNAKE`, private=`_underscore`

**Error Handling**: HTTPException with structured detail

```python
raise HTTPException(status_code=400, detail={"error": "EMPTY_INPUT", "message": "请输入一道数学题"})
```

**Line Length**: 100 characters

## Code Style - TypeScript

**Imports**: react → third-party → local

```typescript
import React, { useState } from "react";
import { HintLayer } from "../types/enums";
import { startSession } from "./services/sessionApi";
```

**Components**: Named exports, interface for props, destructured with defaults

```typescript
interface HintDialogProps {
  problemText: string;
  isLoading?: boolean;
}

export function HintDialog({ problemText, isLoading = false }: HintDialogProps) { ... }
```

**State**: Explicit types when not inferrable

```typescript
const [session, setSession] = useState<SessionState | null>(null);
```

## Test Conventions

### Backend

- **Unit**: `tests/unit/test_*.py` - Service tests with `@pytest.mark.unit`
- **Contract**: `tests/contract/test_*.py` - API tests with `@pytest.mark.contract`
- **Fixtures**: `tests/conftest.py`

```python
class TestConceptHintNoAnswer:
    @pytest.mark.unit
    def test_concept_hint_does_not_contain_numeric_answer(self) -> None:
        generator = HintGenerator()
        hint = generator.generate(...)
        assert "x = 3" not in hint.content
```

### Frontend

- **E2E**: `tests/e2e/*.spec.ts` - Playwright
- Use accessible selectors: `page.getByLabel()`, `page.getByRole()`

## Project Rules (Constitution)

1. **No direct answers** - Hints guide, never reveal solutions
2. **Encouraging language** - Never use "错", "不对", "wrong", "incorrect"
3. **10+ char responses** - Student responses must be ≥10 characters
4. **No raw logging** - Don't log student response text (privacy)

## API Error Format

All 4xx errors: `{"error": "ERROR_CODE", "message": "用户友好消息"}`

## Layer Progression

`CONCEPT` → `STRATEGY` → `STEP` → `COMPLETED`

- UNDERSTOOD: advance layer (reset confusion_count)
- CONFUSED: stay on layer (increment confusion_count)
- 3 confusions: downgrade hint (is_downgrade=true)

## File Structure

```
backend/
├── api/           # FastAPI routers
├── models/        # SQLAlchemy models + enums
├── schemas/       # Pydantic schemas
├── services/      # Business logic
├── database/      # DB engine
└── tests/{unit,contract}/

frontend/src/
├── components/    # React components
├── services/      # API client
├── stores/        # State management
├── types/         # TypeScript enums
└── tests/e2e/     # Playwright tests
```

## TDD Workflow

1. Write failing test → 2. Run (should fail) → 3. Implement → 4. Run (should pass) → 5. Refactor
