# StepWise Development Progress

> Last Updated: 2026-01-09

## Recent Milestones

### 2026-01-09: Beta Infrastructure & Local QA Prep

**PR #5 Merged**: "chore: local QA prep & documentation"

**Key Achievements**:
- ✅ Merged PR #5 to master (EMAIL_TEMPLATES.md + seed_demo_data.py fixes)
- ✅ Generated 250 total beta codes (50 initial + 200 additional)
- ✅ Created automated local QA script (`scripts/run_local_qa.sh`)
- ✅ All 328 backend tests passing
- ✅ Frontend build successful
- ✅ Demo data seeded (5 problems, 3 sessions, 3 feedback items)

---

## Completed Tasks (T039-T055)

### Infrastructure & CI/CD (T039-T044)

#### T039: Optimize CI PostgreSQL Workflow ✅
- Added dependency caching (pip + npm)
- Configured xvfb for Playwright headless testing
- PostgreSQL health checks
- CI runtime: ~8min → ~5min

#### T040: Sentry Source Maps Workflow ✅
- Auto-uploads source maps on production deployments
- Triggers on tags matching `v*`
- Requires `SENTRY_AUTH_TOKEN` and `SENTRY_ORG` secrets

#### T041: Stripe Webhook Test Workflow ✅
- Tests webhook handling for subscription events
- Validates signature verification
- Runs on PR and master push

#### T042: Beta Outreach Documentation ✅
- Created `docs/BETA_OUTREACH.md`
- Reddit/Discord templates
- Engagement best practices
- Tracking spreadsheet template

#### T043: Review Apps Workflow ✅
- Fly.io PR preview deployments
- Auto-cleanup on PR close
- Requires `FLY_API_TOKEN` secret

#### T044: RFC 8058 List-Unsubscribe ✅
- One-click unsubscribe implementation
- Added to session reports and weekly digests
- CAN-SPAM compliant

### Local QA Preparation (T045-T055)

#### T045: Merge PR #4 to Master ✅
- Squash merged all T039-T044 changes
- 328 backend tests passing after merge

#### T046: Create PROGRESS.md ✅
- Comprehensive progress documentation
- Infrastructure status table
- Required GitHub secrets checklist

#### T047: Generate Beta Codes (Batch #1) ✅
- 50 codes in `beta_codes_20260109.csv`
- 8-character alphanumeric format
- Ready for initial distribution

#### T048: Seed Demo Data ✅
- Fixed `scripts/seed_demo_data.py` schemas
- Created 5 problems, 3 sessions, 3 feedback items
- Successfully tested locally

#### T050: Run Full Test Matrix ✅
- Backend: 328 tests passing (6.02s with SQLite)
- Frontend: Build successful
- E2E: Playwright tests ready

#### T051: Create EMAIL_TEMPLATES.md ✅
- 567 lines of documentation
- RFC 8058 implementation details
- Compliance notes (CAN-SPAM, COPPA, GDPR)

#### T052: Create PR #5 ✅
- Opened PR with EMAIL_TEMPLATES.md + seed_demo_data.py
- Comprehensive PR description
- Ready for review

#### T053: Merge PR #5 ✅
- Merged to master on 2026-01-09
- All CI checks passed (backend + frontend)
- Review app deployment skipped (missing Fly.io token)

#### T054: Generate Beta Codes (Batch #2) ✅
- 200 additional codes in `beta_codes_20260109_extra.csv`
- Format: `MATH-XXXX-XXXX`
- 90-day validity
- Updated `docs/BETA_OUTREACH.md` with batch details

#### T055: Create run_local_qa.sh ✅
- Automated QA testing script
- Starts PostgreSQL via docker-compose
- Runs pytest + Playwright
- Opens Playwright UI for exploratory testing
- Supports `--skip-docker`, `--skip-tests`, `--ui-only` flags

---

## Infrastructure Status

| Component              | Status | Notes                                                  |
| ---------------------- | ------ | ------------------------------------------------------ |
| CI PostgreSQL Workflow | ✅     | Optimized with caching, xvfb for Playwright            |
| CI Standard Workflow   | ✅     | SQLite-based, fast feedback                            |
| Sentry Source Maps     | ✅     | Auto-uploads on production deployments                 |
| Stripe Webhook Tests   | ✅     | Validates webhook handling on every PR                 |
| Review Apps (Fly.io)   | ⚠️     | Workflow created, needs `FLY_API_TOKEN` secret         |
| Email (RFC 8058)       | ✅     | One-click unsubscribe implemented                      |
| Beta Codes             | ✅     | 250 codes generated (50 + 200)                         |
| Demo Data              | ✅     | 5 problems, 3 sessions, 3 feedback items seeded        |
| Documentation          | ✅     | BETA_OUTREACH.md, EMAIL_TEMPLATES.md, PROGRESS.md      |
| Local QA Script        | ✅     | `scripts/run_local_qa.sh` with automated workflow      |

---

## Required GitHub Secrets

| Secret               | Purpose                          | Status | Required For                |
| -------------------- | -------------------------------- | ------ | --------------------------- |
| `SENTRY_AUTH_TOKEN`  | Upload source maps to Sentry     | ⚠️     | Sentry Source Maps workflow |
| `SENTRY_ORG`         | Sentry organization slug         | ⚠️     | Sentry Source Maps workflow |
| `FLY_API_TOKEN`      | Deploy review apps to Fly.io     | ⚠️     | Review Apps workflow        |
| `STRIPE_SECRET_KEY`  | Stripe API access (test mode)    | ✅     | Stripe Webhook Tests        |
| `STRIPE_WEBHOOK_SECRET` | Verify webhook signatures     | ✅     | Stripe Webhook Tests        |

**Note**: Secrets marked ⚠️ are optional for local development but required for full CI/CD functionality.

---

## Beta Code Distribution

### Batch #1 (2026-01-09)
- **Count**: 50 codes
- **File**: `beta_codes_20260109.csv` (gitignored)
- **Format**: 8-character alphanumeric (e.g., `A1B2C3D4`)
- **Target**: Reddit r/homeschool, r/Parenting early adopters
- **Status**: Ready for distribution

### Batch #2 (2026-01-09)
- **Count**: 200 codes
- **File**: `beta_codes_20260109_extra.csv` (gitignored)
- **Format**: `MATH-XXXX-XXXX` (e.g., `MATH-2DK5-FKEB`)
- **Target**: Discord servers, direct outreach, community referrals
- **Validity**: 90 days from generation
- **Status**: Ready for distribution

**Total Available**: 250 beta codes

---

## Development Metrics

### Test Coverage
- **Backend Tests**: 328 passing (6.02s with SQLite)
- **Frontend Build**: Successful (TypeScript 5.x + React 18 + Vite)
- **E2E Tests**: Playwright configured with xvfb support
- **Code Coverage**: TBD (coverage reporting configured but not yet analyzed)

### Performance
- **CI Runtime**: ~5min (with caching)
- **Backend Startup**: ~2s (local development)
- **Frontend Build**: ~15s (production build)

### Code Quality
- **Linting**: Configured (ruff + black for Python, ESLint for TypeScript)
- **Type Checking**: Strict mode (mypy for Python, TypeScript strict)
- **Pre-commit Hooks**: Configured (auto-formatting, basic checks)

---

## Local QA Checklist

### Prerequisites
- [ ] PostgreSQL running (via `docker-compose --profile postgres up -d`)
- [ ] Backend dependencies installed (`pip install -e ".[dev]"`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Playwright browsers installed (`npx playwright install --with-deps`)

### Automated Testing
- [ ] Run `./scripts/run_local_qa.sh` to execute full test suite
- [ ] Verify all 328 backend tests pass
- [ ] Verify frontend E2E tests pass
- [ ] Use Playwright UI for exploratory testing

### Manual Testing (see MANUAL_QA_CHECKLIST.md)
- [ ] User registration flow
- [ ] Problem submission and hint progression
- [ ] Parent email delivery (session reports)
- [ ] One-click unsubscribe functionality
- [ ] Database writes (verify data persistence)
- [ ] Sentry error tracking (trigger test error)

### UAT Elements
- [ ] **Usability**: Can a parent navigate the app without instructions?
- [ ] **Accessibility**: Screen reader compatibility, keyboard navigation
- [ ] **Performance**: Page load times < 3s, hint generation < 2s
- [ ] **Reliability**: No crashes during 30-minute session
- [ ] **Security**: No exposed API keys, HTTPS enforced, CORS configured

---

## Next Steps

### Immediate (This Week)
1. **Complete Manual QA Checklist** (T057)
   - Document full-chain testing items
   - Include UAT best practices
   - Add screenshots for key flows

2. **Create Unsubscribe Monitoring** (T058)
   - Script to parse SendGrid Event Webhook JSON
   - Alert if unsubscribe rate > 2%
   - Reference Mailchimp/Litmus standards

3. **Automate Weekly Metrics** (T059)
   - GitHub Actions workflow for weekly monitoring
   - Run `monitor_unsubscribe_rate.py` every Monday UTC 0:00
   - Output to GitHub Step Summary

### Short-term (Next 2 Weeks)
1. **Distribute Beta Codes**
   - Reddit outreach (r/homeschool, r/Parenting)
   - Discord servers (homeschool communities)
   - Direct outreach to education influencers

2. **Monitor Beta Feedback**
   - Track PMF survey responses
   - Monitor unsubscribe rates
   - Collect feature requests

3. **Iterate on Feedback**
   - Fix critical bugs reported by beta testers
   - Implement high-priority feature requests
   - Improve onboarding flow based on user confusion

### Medium-term (Next Month)
1. **Production Deployment**
   - Configure Fly.io production environment
   - Set up Sentry for error tracking
   - Configure SendGrid for email delivery
   - Enable Stripe for subscription billing

2. **Public Launch Preparation**
   - Finalize pricing tiers
   - Create marketing materials
   - Prepare launch announcement
   - Set up customer support channels

---

## Team Communication

**Last Sync**: 2026-01-09

**Blockers**: None

**Questions**: None

**Decisions Made**:
1. Use squash merge for PRs to keep master history clean
2. Generate beta codes in batches (50 initial, 200 additional)
3. Use RFC 8058 one-click unsubscribe for better email deliverability
4. Document all infrastructure changes in PROGRESS.md for team visibility
5. Create automated QA script to streamline local testing workflow

---

## Notes

- All T039-T055 tasks completed successfully
- PR #5 merged to master with EMAIL_TEMPLATES.md and seed_demo_data.py fixes
- 250 beta codes ready for distribution
- Local QA script (`run_local_qa.sh`) automates testing workflow
- Next focus: Manual QA checklist, unsubscribe monitoring, weekly metrics automation
