# StepWise Development Progress

> **Last Updated**: 2026-01-09

---

## 2026-01-09 – CI/CD Infrastructure & Beta Preparation

### Completed Tasks (T039-T044)

#### T039: Optimize ci_postgres.yml

- ✅ Added pip cache for Python dependencies
- ✅ Added npm cache for Node.js dependencies
- ✅ Added Playwright browser cache
- ✅ Wrapped Playwright tests in `xvfb-run` for headless execution
- ✅ PostgreSQL 16 service with health checks
- ⚠️ Running tests sequentially (not `-n auto`) to avoid PostgreSQL ENUM type race conditions

#### T040: Sentry Source Maps Workflow

- ✅ Created `.github/workflows/sentry_sourcemaps.yml`
- ✅ Uploads Vite-generated source maps to Sentry
- ✅ Sets `SENTRY_RELEASE=${{ github.sha }}` for release tracking
- ✅ Creates Sentry releases with git commit metadata
- ✅ Triggers on push to `main` branch

#### T041: Stripe Webhook Test Workflow

- ✅ Created `.github/workflows/stripe_webhook_test.yml`
- ✅ Uses `stripe/stripe-cli-action` for webhook testing
- ✅ Triggers test events: `payment_intent.succeeded`, `checkout.session.completed`, subscription events
- ✅ Runs webhook signature verification tests
- ✅ PostgreSQL 16 service for integration tests

#### T042: Beta Outreach Documentation

- ✅ Created `docs/BETA_OUTREACH.md`
- ✅ Reddit templates for r/Parenting, r/homeschool, r/learnmath, r/education
- ✅ Discord community templates
- ✅ Email invite templates
- ✅ PMF (Product-Market Fit) survey structure
- ✅ CAN-SPAM compliant email footers
- ✅ COPPA-aware messaging

#### T043: PR Review Apps Workflow

- ✅ Created `.github/workflows/review_apps.yml`
- ✅ Uses `superfly/fly-pr-review-apps@1.2.1`
- ✅ Deploys ephemeral backend and frontend apps per PR
- ✅ Auto-comments PR with review app URLs
- ✅ Auto-destroys apps when PR is closed
- ⚠️ Requires `FLY_API_TOKEN` secret to be configured

#### T044: One-Click Unsubscribe (RFC 8058)

- ✅ `/api/v1/email/unsubscribe/{token}` endpoint already existed
- ✅ Added `list_unsubscribe` and `list_unsubscribe_post` fields to `EmailMessage` class
- ✅ SendGrid provider now sets `List-Unsubscribe` and `List-Unsubscribe-Post` headers
- ✅ Session reports include one-click unsubscribe header
- ✅ Weekly digests include one-click unsubscribe header
- ✅ All 328 backend tests passing

### Infrastructure Status

| Component              | Status     | Notes                           |
| ---------------------- | ---------- | ------------------------------- |
| **CI (SQLite)**        | ✅ Passing | 328 tests, ~6s                  |
| **CI (PostgreSQL)**    | ✅ Passing | 328 tests, sequential execution |
| **Frontend Build**     | ✅ Passing | TypeScript + Vite               |
| **E2E Tests**          | ✅ Passing | Playwright with xvfb            |
| **Sentry Integration** | ⚠️ Ready   | Needs secrets configured        |
| **Stripe Webhooks**    | ⚠️ Ready   | Needs secrets configured        |
| **Fly.io Review Apps** | ⚠️ Ready   | Needs `FLY_API_TOKEN`           |

### Required GitHub Secrets

To enable all workflows, configure these secrets at:
https://github.com/412984588/stepwise/settings/secrets/actions

| Secret                       | Purpose                          | Status     |
| ---------------------------- | -------------------------------- | ---------- |
| `FLY_API_TOKEN`              | Fly.io deployments & review apps | ❌ Not set |
| `SENTRY_ORG`                 | Sentry organization name         | ❌ Not set |
| `SENTRY_PROJECT`             | Sentry project name              | ❌ Not set |
| `SENTRY_AUTH_TOKEN`          | Sentry API token                 | ❌ Not set |
| `VITE_SENTRY_DSN`            | Frontend Sentry DSN              | ❌ Not set |
| `STRIPE_TEST_SECRET_KEY`     | Stripe test mode key             | ❌ Not set |
| `STRIPE_TEST_WEBHOOK_SECRET` | Stripe webhook signing secret    | ❌ Not set |
| `OPENAI_API_KEY`             | OpenAI API key                   | ✅ Set     |

---

## 2026-01-09 – Beta Code Generation (T047)

### Beta Access Codes

- ✅ Generated 50 beta codes using `scripts/generate_beta_codes.py`
- ✅ Format: `MATH-XXXX-XXXX` (8-character random suffix)
- ✅ Saved to `beta_codes_20260109.csv` (not committed to git)
- ✅ Added `beta_codes_*.csv` to `.gitignore`
- ✅ Codes valid for 90 days from generation

### Usage

```bash
# Generate more codes
python3 scripts/generate_beta_codes.py -n 100 -o beta_codes_$(date +%Y%m%d).csv

# View generated codes
cat beta_codes_20260109.csv
```

---

## Development Metrics

| Metric               | Value       | Date       |
| -------------------- | ----------- | ---------- |
| Backend Tests        | 328 passing | 2026-01-09 |
| Frontend Build Time  | ~450ms      | 2026-01-09 |
| E2E Test Coverage    | Core flows  | 2026-01-09 |
| GitHub Workflows     | 6 active    | 2026-01-09 |
| Beta Codes Generated | 50          | 2026-01-09 |

---

_This document tracks major milestones and infrastructure changes. For detailed commit history, see `git log`._
