# StepWise - Socratic Math Tutoring System

> **🇺🇸 US Private Beta** | [Join the Beta](./docs/US_PRIVATE_BETA.md) | [Release v0.1.1](https://github.com/your-org/StepWise/releases/tag/v0.1.1)

## What is StepWise?

StepWise is a Socratic-style math tutoring system designed for **US families with students in Grades 4–9**. Instead of giving away answers, StepWise guides students through problem-solving with layered hints—starting with conceptual guidance, then strategic approaches, and finally step-by-step help if needed.

**For Parents**: Receive session reports after each learning session and weekly digests summarizing your child's progress. No accounts required—just provide your email to receive reports.

## Features

- **Layered Hints**: Concept → Strategy → Step progression
- **Progress Dashboard**: Track learning stats and trends
- **Email Reports**: Session summaries and weekly digests to parents
- **Grade-based Content**: Grades 4-9 math problems
- **Privacy-first**: Children's data minimized; no accounts required

## Quick Start

The fastest way to run StepWise locally:

```bash
# Clone the repository
git clone https://github.com/your-org/StepWise.git
cd StepWise

# Start both backend and frontend
./scripts/dev_up.sh

# Open http://localhost:3000 in your browser

# When done, stop the servers
./scripts/dev_down.sh
```

### Prerequisites

- Python 3.11+
- Node.js 18+

## Documentation

- **[US Private Beta Guide](./docs/US_PRIVATE_BETA.md)** - For beta testers: what StepWise does, how to run it, privacy info
- **[Privacy Policy](./docs/PRIVACY_POLICY.md)** - How we handle data (COPPA-compliant)
- **[Terms of Service](./docs/TERMS_OF_SERVICE.md)** - Usage terms
- **[Production Runbook](./docs/PRODUCTION_RUNBOOK.md)** - Deployment and operations guide
- **[Release Notes](./docs/RELEASE_NOTES.md)** - What's new in each release

## Tech Stack

- **Backend**: Python 3.11 + FastAPI + SQLAlchemy + SQLite
- **Frontend**: TypeScript 5.x + React 18 + Vite
- **Testing**: pytest (backend), Playwright (frontend E2E)

## Detailed Setup

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -e ".[dev]"

# Create .env file (copy from .env.example)
cp .env.example .env

# Edit .env and add your keys:
# - OPENAI_API_KEY (required for hint generation)

# Run tests
pytest tests/ -v

# Start development server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Testing the Full Flow

1. **Open the frontend** at `http://localhost:3000`
2. **Select your child's grade level**
3. **Enter a math problem** (e.g., "Solve 2x + 5 = 11")
4. **Follow the hints** - respond with your understanding
5. **Provide your email** (optional) to receive a learning report

## Feedback

We'd love to hear from you! Use the **Feedback** button in the app or see our [Feedback Form Spec](./docs/US_BETA_FEEDBACK.md).

## License

MIT

## Project Structure

```
StepWise/
├── backend/
│   ├── api/              # FastAPI routers
│   │   ├── sessions.py   # Hint session endpoints
│   │   ├── billing.py    # Stripe billing endpoints
│   │   └── stats.py      # Statistics endpoints
│   ├── models/           # SQLAlchemy models
│   │   ├── problem.py
│   │   ├── hint_session.py
│   │   └── subscription.py
│   ├── services/         # Business logic
│   │   ├── hint_generator.py
│   │   ├── stripe_service.py
│   │   └── entitlements.py
│   ├── tests/
│   │   ├── unit/         # Unit tests
│   │   └── contract/     # API contract tests
│   └── pyproject.toml
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── HintDialog.tsx
    │   │   ├── SubscriptionBanner.tsx
    │   │   └── UpgradeModal.tsx
    │   ├── services/
    │   │   ├── sessionApi.ts
    │   │   └── billingApi.ts
    │   ├── hooks/
    │   │   └── useUserId.ts
    │   └── i18n/
    │       └── locales/
    │           ├── en-US.json
    │           └── zh-CN.json
    └── package.json
```

## API Endpoints

### Session Management

- `POST /api/v1/sessions/start` - Start a new hint session
- `POST /api/v1/sessions/{session_id}/respond` - Respond to a hint
- `POST /api/v1/sessions/{session_id}/reveal` - Reveal the solution
- `POST /api/v1/sessions/{session_id}/complete` - Mark session as complete

### Billing

- `GET /api/v1/billing/subscription` - Get user's subscription status
- `POST /api/v1/billing/checkout` - Create Stripe checkout session
- `POST /api/v1/billing/portal` - Create Stripe customer portal session
- `POST /api/v1/billing/webhook` - Stripe webhook handler
- `GET /api/v1/billing/usage` - Get user's daily usage

### Statistics

- `GET /api/v1/stats/summary` - Get user statistics summary
- `GET /api/v1/stats/dashboard` - Get dashboard data
- `GET /api/v1/stats/trend` - Get trend data
- `GET /api/v1/stats/goals` - Get goal progress

## Subscription Tiers

| Tier       | Price     | Daily Limit    | Features                                  |
| ---------- | --------- | -------------- | ----------------------------------------- |
| **Free**   | $0        | 3 problems/day | Basic hints, concept/strategy/step layers |
| **Pro**    | $9.99/mo  | Unlimited      | All features, priority support            |
| **Family** | $19.99/mo | Unlimited      | Pro features + up to 5 user profiles      |

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run unit tests only
pytest tests/unit/ -v

# Run contract tests only
pytest tests/contract/ -v

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_entitlements.py -v
```

### Frontend Tests

```bash
cd frontend

# Type check and build
npm run build

# Lint
npm run lint

# E2E tests (requires backend running)
npx playwright test
```

## Environment Variables

### Backend (.env)

```bash
# Required
OPENAI_API_KEY=sk-your-openai-api-key-here
DATABASE_URL=sqlite:///./stepwise.db

# Optional (development)
DEBUG=true
LOG_LEVEL=INFO

# Stripe (required for billing features)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
STRIPE_PRO_PRICE_ID=price_your_pro_price_id_here
STRIPE_FAMILY_PRICE_ID=price_your_family_price_id_here
```

### Frontend (.env)

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Deployment

### Stripe Setup

1. **Create Products in Stripe Dashboard**:
   - Pro: $9.99/month recurring
   - Family: $19.99/month recurring

2. **Get Price IDs** from Stripe Dashboard and add to backend `.env`

3. **Set up Webhook**:
   - URL: `https://yourapp.com/api/v1/billing/webhook`
   - Events to listen for:
     - `checkout.session.completed`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`

4. **Get Webhook Secret** and add to backend `.env`

### Database Migration

For production, migrate from SQLite to PostgreSQL:

```bash
# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@host:5432/stepwise

# SQLAlchemy will auto-create tables on first run
```

## Development Guidelines

See [AGENTS.md](./AGENTS.md) for detailed development guidelines including:

- Code style conventions
- Testing workflow (TDD)
- Build commands
- Project rules and constraints

## License

MIT
