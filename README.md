# StepWise - Socratic Math Tutoring System

A layered hint system for math education that guides students through problem-solving using Socratic questioning.

## Features

- **Layered Hints**: Concept → Strategy → Step progression
- **Subscription Tiers**: Free (3 problems/day), Pro ($9.99/mo), Family ($19.99/mo)
- **Stripe Billing**: Full payment and subscription management
- **Internationalization**: English (en-US) and Chinese (zh-CN) support
- **Grade-based Content**: Grades 4-9 math problems

## Tech Stack

- **Backend**: Python 3.11 + FastAPI + SQLAlchemy + SQLite
- **Frontend**: TypeScript 5.x + React 18 + Vite
- **Payments**: Stripe API
- **Testing**: pytest (backend), Playwright (frontend E2E)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Stripe account (for production)

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -e ".[dev]"

# Create .env file (copy from .env.example)
cp .env.example .env

# Edit .env and add your keys:
# - OPENAI_API_KEY (required for hint generation)
# - STRIPE_SECRET_KEY (for billing, use test keys for development)
# - STRIPE_WEBHOOK_SECRET (for webhook verification)
# - STRIPE_PRO_PRICE_ID (Stripe price ID for Pro tier)
# - STRIPE_FAMILY_PRICE_ID (Stripe price ID for Family tier)

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

Frontend will be available at `http://localhost:3001` (or next available port)

### Testing the Full Flow

1. **Open the frontend** at `http://localhost:3001`
2. **Enter a math problem** (e.g., "Solve 2x + 5 = 11")
3. **Interact with hints** - try "明白了" (understood) or "不懂" (confused)
4. **Test the free tier limit**:
   - Create 3 sessions (free tier limit)
   - On the 4th attempt, you should see the upgrade modal
5. **Test subscription UI**:
   - Click "Upgrade" to see pricing tiers
   - Subscription banner shows current tier and usage

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

| Tier | Price | Daily Limit | Features |
|------|-------|-------------|----------|
| **Free** | $0 | 3 problems/day | Basic hints, concept/strategy/step layers |
| **Pro** | $9.99/mo | Unlimited | All features, priority support |
| **Family** | $19.99/mo | Unlimited | Pro features + up to 5 user profiles |

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
