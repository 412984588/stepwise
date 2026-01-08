# StepWise Release Notes

## Version 1.0.0 (January 2025)

**Release Name**: Release & Runbook Pack

---

## Feature Set Summary

### Core Learning System

| Feature                    | Description                                                                               |
| -------------------------- | ----------------------------------------------------------------------------------------- |
| **Layered Hints**          | Socratic-style progression: Concept → Strategy → Step                                     |
| **Confusion Detection**    | Adaptive hints based on student responses                                                 |
| **Problem Classification** | Automatic detection of problem types (linear equations, quadratics, geometry, arithmetic) |
| **Solution Reveal**        | Full step-by-step solutions available after working through hints                         |
| **Grade-based Content**    | Support for grades 4-9 math curriculum                                                    |

### Parent Dashboard

| Feature                 | Description                                             |
| ----------------------- | ------------------------------------------------------- |
| **Learning Statistics** | Total days, completion rates, weekly practice, streaks  |
| **Goal Progress**       | Daily and weekly goals with visual progress rings       |
| **Practice Trend**      | 7-day chart showing independent vs total problems       |
| **Session History**     | Recent sessions with layer reached and confusion counts |
| **PDF Reports**         | Downloadable session reports with learning summary      |
| **Encouragement**       | Personalized messages based on performance              |

### Email System

| Feature                   | Description                                               |
| ------------------------- | --------------------------------------------------------- |
| **Session Reports**       | Automatic email with PDF attachment on session completion |
| **Weekly Digest**         | Aggregated weekly progress summary                        |
| **Unsubscribe**           | Granular control (session reports, weekly digest, or all) |
| **Send-time Suppression** | Respects preferences at send time                         |
| **Idempotency**           | Prevents duplicate email sends                            |

### Billing (Stripe Integration)

| Tier   | Price     | Daily Limit | Features                |
| ------ | --------- | ----------- | ----------------------- |
| Free   | $0        | 3 problems  | Basic hints, all layers |
| Pro    | $9.99/mo  | Unlimited   | Priority support        |
| Family | $19.99/mo | Unlimited   | Up to 5 user profiles   |

### Internationalization

| Language | Locale  |
| -------- | ------- |
| English  | `en-US` |
| Chinese  | `zh-CN` |

---

## Security Posture Summary

### Authentication

| Mechanism             | Scope           | Details                                           |
| --------------------- | --------------- | ------------------------------------------------- |
| **API Key**           | Admin endpoints | `X-API-Key` header, env-configurable              |
| **Session Token**     | PDF downloads   | Per-session UUID, `X-Session-Access-Token` header |
| **Unsubscribe Token** | Email prefs     | Per-email UUID, URL-based                         |

### Rate Limiting

| Layer              | Implementation           | Limits                                       |
| ------------------ | ------------------------ | -------------------------------------------- |
| **API endpoints**  | In-memory sliding window | 20 req/60s per IP                            |
| **Email throttle** | Database-backed          | 5 session reports/24h, 1 digest/7d per email |

### Data Protection

- Session tokens prevent unauthorized PDF access
- No logging of student response text (privacy)
- Email preferences stored with secure unsubscribe tokens
- Idempotency keys prevent duplicate operations

### Abuse Prevention

- Per-email throttling with configurable limits
- Rate limiting on all stats/reports endpoints
- Retry-After headers for 429 responses
- Email send logging for audit trail

---

## Testing Status

### Backend Tests

```
======================== 267 passed, 4 skipped ========================
```

| Category       | Status       | Notes                         |
| -------------- | ------------ | ----------------------------- |
| Unit tests     | ✅ Pass      | All services tested           |
| Contract tests | ✅ Pass      | API contracts verified        |
| Email service  | ⏭️ 4 skipped | SendGrid tests require config |

### E2E Tests (Playwright)

```
======================== 38 passed ========================
```

| Category        | Status  | Tests    |
| --------------- | ------- | -------- |
| Hint Flow       | ✅ Pass | 18 tests |
| Dashboard Flow  | ✅ Pass | 6 tests  |
| Reveal Solution | ✅ Pass | 5 tests  |
| Email Reports   | ✅ Pass | 7 tests  |
| PDF Reports     | ✅ Pass | 2 tests  |

### Test Commands

```bash
# Backend tests (no env prefix needed - autouse fixture sets vars)
cd backend && python3 -m pytest tests/ -q

# Frontend E2E (auto-starts servers via playwright.config.ts)
cd frontend && npm test

# Run specific test
cd backend && python3 -m pytest tests/unit/test_hint_generator.py -v
cd frontend && npx playwright test tests/e2e/hint-flow.spec.ts
```

---

## Known Limitations

### Optional Dependencies

| Dependency | Status            | Impact                                 |
| ---------- | ----------------- | -------------------------------------- |
| SendGrid   | Optional          | 4 tests skipped when not configured    |
| Stripe     | Optional          | Billing features disabled without keys |
| OpenAI     | Required for prod | Hint generation fails without API key  |

### Database

| Limitation     | Details                                          |
| -------------- | ------------------------------------------------ |
| SQLite default | Use PostgreSQL for production                    |
| No migrations  | `alembic upgrade head` needed for schema changes |

### Email

| Limitation       | Details                                 |
| ---------------- | --------------------------------------- |
| Console provider | Development only, logs to stdout        |
| No retry queue   | Failed sends not automatically retried  |
| Single provider  | No fallback to secondary email provider |

### Rate Limiting

| Limitation        | Details                         |
| ----------------- | ------------------------------- |
| In-memory for API | Resets on server restart        |
| Per-IP only       | No user-based API rate limiting |

---

## Upgrade Instructions

### From Development to Production

1. **Environment Variables**

```bash
# Required
export API_ACCESS_KEY="sk_prod_your_secret_key"
export DATABASE_URL="postgresql://user:pass@host:5432/stepwise"
export OPENAI_API_KEY="sk-your-openai-key"

# Email (choose one)
export EMAIL_PROVIDER="sendgrid"
export SENDGRID_API_KEY="SG.xxxxx"
export EMAIL_FROM="noreply@yourdomain.com"
export API_BASE_URL="https://yourdomain.com"

# Optional: Stripe
export STRIPE_SECRET_KEY="sk_live_xxxxx"
export STRIPE_WEBHOOK_SECRET="whsec_xxxxx"
```

2. **Database Migration**

```bash
cd backend
alembic upgrade head
```

3. **Verify Health**

```bash
curl https://yourdomain.com/docs  # Should return Swagger UI
curl -H "X-API-Key: $API_ACCESS_KEY" \
  https://yourdomain.com/api/v1/stats/summary
```

### Version Compatibility

| Component  | Required Version |
| ---------- | ---------------- |
| Python     | 3.11+            |
| Node.js    | 18+              |
| PostgreSQL | 14+ (production) |

---

## File Structure

```
StepWise/
├── backend/
│   ├── api/              # FastAPI routers
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── tests/            # pytest tests
│   └── scripts/          # Admin scripts
├── frontend/
│   ├── src/              # React components
│   ├── tests/e2e/        # Playwright tests
│   └── playwright.config.ts
├── docs/
│   ├── PRODUCTION_RUNBOOK.md
│   ├── RELEASE_NOTES.md
│   └── SECURITY_POSTURE.md
└── scripts/
    ├── dev_up.sh         # Start dev servers
    ├── dev_down.sh       # Stop dev servers
    └── digest_dry_run.sh # Test weekly digest
```

---

## Quick Start

### Development

```bash
# One command to start everything
./scripts/dev_up.sh

# Visit
# - Frontend: http://127.0.0.1:3000
# - Backend:  http://127.0.0.1:8000
# - API Docs: http://127.0.0.1:8000/docs

# Stop all
./scripts/dev_down.sh
```

### Run Tests

```bash
# Backend
cd backend && python3 -m pytest tests/ -q

# Frontend E2E
cd frontend && npm test
```

---

## Changelog

### v1.0.0 (January 2025)

**Added**

- Production runbook documentation
- Development start/stop scripts
- Weekly digest dry-run script
- CI workflow documentation
- Deterministic test environment (autouse fixtures)

**Fixed**

- Dashboard E2E tests stability (data-testid selectors)
- PDF download button in session history
- TrendChart English text for E2E tests
- GoalProgress achievedText prop cleanup

**Security**

- API key protection on admin endpoints
- Session token validation for PDF downloads
- Email throttling per recipient
- Rate limiting on stats/reports endpoints

---

## Support

- **Issues**: File on project repository
- **Documentation**: See `docs/PRODUCTION_RUNBOOK.md`
- **Security**: See `docs/SECURITY_POSTURE.md`
