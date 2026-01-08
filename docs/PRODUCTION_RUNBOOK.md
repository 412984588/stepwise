# StepWise Production Runbook

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [Authentication & Session Tokens](#authentication--session-tokens)
3. [Email Flows](#email-flows)
4. [Abuse Protection](#abuse-protection)
5. [Troubleshooting](#troubleshooting)

---

## Environment Variables

### Required for Production

| Variable         | Description                                                                         | Example                                     |
| ---------------- | ----------------------------------------------------------------------------------- | ------------------------------------------- |
| `API_ACCESS_KEY` | API key for protected endpoints (`/stats/summary`, `/reports/session/{id}/summary`) | `sk_prod_xxxxxxxxxxxx`                      |
| `DATABASE_URL`   | Database connection string                                                          | `postgresql://user:pass@host:5432/stepwise` |
| `OPENAI_API_KEY` | OpenAI API key for hint generation                                                  | `sk-xxxxxxxx`                               |

### Email Configuration

| Variable           | Description                                      | Default                        |
| ------------------ | ------------------------------------------------ | ------------------------------ |
| `EMAIL_PROVIDER`   | Email backend (`console` or `sendgrid`)          | `console`                      |
| `SENDGRID_API_KEY` | SendGrid API key (required if provider=sendgrid) | -                              |
| `EMAIL_FROM`       | Sender email address                             | `noreply@stepwise.example.com` |
| `API_BASE_URL`     | Base URL for unsubscribe links                   | `http://localhost:8000`        |

### Stripe Billing (Optional)

| Variable                 | Description                   |
| ------------------------ | ----------------------------- |
| `STRIPE_SECRET_KEY`      | Stripe secret key             |
| `STRIPE_WEBHOOK_SECRET`  | Stripe webhook signing secret |
| `STRIPE_PRO_PRICE_ID`    | Price ID for Pro tier         |
| `STRIPE_FAMILY_PRICE_ID` | Price ID for Family tier      |

### Rate Limiting

Rate limits are configured in code (`backend/services/rate_limiter.py`):

| Endpoint Type     | Max Requests | Window     |
| ----------------- | ------------ | ---------- |
| Stats endpoints   | 20           | 60 seconds |
| Reports endpoints | 20           | 60 seconds |

---

## Authentication & Session Tokens

### API Key Protection

Protected endpoints require the `X-API-Key` header:

- `GET /api/v1/stats/summary` - Admin statistics
- `GET /api/v1/reports/session/{id}/summary` - Learning summary JSON

```bash
curl -H "X-API-Key: $API_ACCESS_KEY" \
  http://localhost:8000/api/v1/stats/summary
```

### Session Access Token

Each hint session generates a unique `session_access_token` (UUID) at creation. This token:

1. **Generated**: When `POST /api/v1/sessions/start` is called
2. **Returned**: In the response body as `session_access_token`
3. **Required**: For downloading PDF reports via `GET /api/v1/reports/session/{id}/pdf`

#### Token Flow

```
Browser                         Backend
   |                              |
   |--POST /sessions/start------->|
   |                              | Generate session_access_token
   |<-----{session_access_token}--|
   |                              |
   | (Store token in memory)      |
   |                              |
   |--GET /reports/{id}/pdf------>|
   |  Header: X-Session-Access-Token
   |                              | Verify token matches session
   |<--------PDF binary-----------|
```

#### Endpoints Requiring Session Token

| Endpoint                               | Header                   | Purpose             |
| -------------------------------------- | ------------------------ | ------------------- |
| `GET /api/v1/reports/session/{id}/pdf` | `X-Session-Access-Token` | PDF report download |

#### Error Responses

- **403 MISSING_SESSION_TOKEN**: Token header not provided
- **403 INVALID_SESSION_TOKEN**: Token doesn't match session
- **404 SESSION_NOT_FOUND**: Session ID doesn't exist

---

## Email Flows

### 1. Session Report Email

Triggered when a session is completed with a parent email.

**Flow**:

1. User completes session via `POST /api/v1/sessions/{id}/complete` with `parent_email`
2. Backend generates learning summary and PDF report
3. Email sent with PDF attachment

**Endpoint**: `POST /api/v1/sessions/{session_id}/complete`

```json
{
  "parent_email": "parent@example.com"
}
```

### 2. Weekly Digest

Aggregates learning progress over 7 days for each registered parent email.

**Script**: `backend/scripts/send_weekly_digest.py`

```bash
# Dry-run mode (no emails sent)
cd backend && python scripts/send_weekly_digest.py --dry-run

# Production run
cd backend && python scripts/send_weekly_digest.py

# Custom date range
cd backend && python scripts/send_weekly_digest.py --start-date 2025-01-01
```

**Cron Example** (Sunday 9 AM):

```cron
0 9 * * 0 cd /opt/stepwise/backend && /opt/stepwise/venv/bin/python scripts/send_weekly_digest.py >> /var/log/stepwise/digest.log 2>&1
```

### 3. Unsubscribe Semantics

Parents can unsubscribe via links in emails. Three unsubscribe types:

| Type              | URL Parameter           | Effect                              |
| ----------------- | ----------------------- | ----------------------------------- |
| `weekly_digest`   | `?type=weekly_digest`   | Stop weekly summary emails only     |
| `session_reports` | `?type=session_reports` | Stop per-session report emails only |
| `all`             | `?type=all`             | Stop all StepWise emails            |

**Unsubscribe URL Format**:

```
{API_BASE_URL}/api/v1/email/unsubscribe/{token}?type={type}
```

### 4. Send-Time Suppression

Emails are suppressed at send time (not at preference change time). This means:

1. **Check happens**: When `EmailService.send_learning_report()` or `send_weekly_digest()` is called
2. **Preference lookup**: `EmailPreferenceService.is_session_reports_enabled()` or `is_weekly_digest_enabled()`
3. **Suppressed emails**: Return `True` (success) without sending - prevents breaking upstream flows
4. **Logged**: "Email suppressed: {type} disabled for {email}"

**Why send-time suppression?**

- Batch jobs don't need to pre-filter recipients
- Preference changes take effect immediately
- Single source of truth for email eligibility

---

## Abuse Protection

### Per-Email Throttling

Enforced in `EmailThrottleService` to prevent email bombing:

| Email Type      | Limit | Window   |
| --------------- | ----- | -------- |
| Session Reports | 5     | 24 hours |
| Weekly Digest   | 1     | 7 days   |

**Implementation**: `backend/services/email_throttle_service.py`

When limit exceeded:

- Returns HTTP 429 Too Many Requests
- Response includes `retry_after` seconds
- Response includes `limit` and `window` for debugging

```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many session reports sent. Please try again later.",
  "retry_after": 3600,
  "limit": 5,
  "window": "24 hours"
}
```

### API Rate Limiting

General endpoint rate limiting via sliding window:

| Endpoint Group | Limit       | Window     | Retry-After Header |
| -------------- | ----------- | ---------- | ------------------ |
| `/stats/*`     | 20 requests | 60 seconds | Yes                |
| `/reports/*`   | 20 requests | 60 seconds | Yes                |

When rate limited:

```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests. Please try again in 45 seconds.",
  "retry_after": 45
}
```

### Idempotency

Duplicate email sends are prevented via `EmailSendLog`:

1. **Idempotency key**: Generated from `(email, type, session_id or week_start_date)`
2. **Check**: Before sending, query for existing SENT record with same key
3. **Skip**: If found, return success without sending
4. **Log**: "Idempotent skip: {type} already sent for {id} to {email} at {timestamp}"

---

## Troubleshooting

### No Email Received

**1. Check EMAIL_PROVIDER setting**

```bash
# Should be 'sendgrid' for production
echo $EMAIL_PROVIDER

# If 'console', emails are logged to stdout only
grep "CONSOLE EMAIL PROVIDER" /var/log/stepwise/app.log
```

**2. Verify SendGrid configuration**

```bash
# Check API key is set
[ -n "$SENDGRID_API_KEY" ] && echo "Set" || echo "NOT SET"

# Check FROM address
echo $EMAIL_FROM
```

**3. Check email preference**

```sql
-- Check if user is subscribed
SELECT * FROM email_preferences WHERE email = 'parent@example.com';

-- weekly_digest_enabled should be true
-- session_reports_enabled should be true
```

**4. Check throttle status**

```sql
-- Check recent throttle records
SELECT * FROM email_throttles
WHERE email = 'parent@example.com'
ORDER BY created_at DESC LIMIT 5;
```

### Unsubscribe Still Receiving

**1. Verify preference was saved**

```sql
SELECT email, weekly_digest_enabled, session_reports_enabled,
       weekly_digest_unsubscribed_at, session_reports_unsubscribed_at
FROM email_preferences
WHERE email = 'parent@example.com';
```

**2. Check if correct type was unsubscribed**

- Unsubscribing from `weekly_digest` doesn't affect `session_reports`
- Use `?type=all` to unsubscribe from everything

**3. Check for multiple preference records**

```sql
SELECT COUNT(*), email FROM email_preferences
GROUP BY email HAVING COUNT(*) > 1;
```

### Duplicate Send Investigation

**1. Query EmailSendLog**

```sql
SELECT id, email, email_type, session_id, week_start_date,
       status, sent_at, created_at, idempotency_key
FROM email_send_logs
WHERE email = 'parent@example.com'
ORDER BY created_at DESC LIMIT 20;
```

**2. Check for SENT records with same idempotency_key**

```sql
SELECT idempotency_key, COUNT(*)
FROM email_send_logs
WHERE status = 'sent'
GROUP BY idempotency_key
HAVING COUNT(*) > 1;
```

**3. Check for race conditions**
Look for multiple PENDING records created within milliseconds:

```sql
SELECT * FROM email_send_logs
WHERE email = 'parent@example.com'
  AND created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at;
```

### 429 Too Aggressive

**1. Check current rate limit config**

API rate limits (in-memory, resets on restart):

```python
# backend/services/rate_limiter.py
RateLimitConfig(max_requests=20, window_seconds=60)
```

Email throttle limits (database-backed):

```python
# backend/services/email_throttle_service.py
SESSION_REPORT_LIMIT = 5   # per 24 hours
WEEKLY_DIGEST_LIMIT = 1    # per 7 days
```

**2. Reset throttle for testing**

```sql
-- Clear throttle records for a specific email
DELETE FROM email_throttles WHERE email = 'test@example.com';
```

**3. Reset rate limiter (requires restart or code)**
Rate limiters reset automatically when the server restarts. For testing:

```python
from backend.services.rate_limiter import get_stats_rate_limiter
get_stats_rate_limiter().reset()
```

---

## Health Checks

### Backend Health

```bash
curl http://localhost:8000/docs
# Should return Swagger UI
```

### Database Connection

```bash
curl http://localhost:8000/api/v1/stats/dashboard
# Should return 200 with dashboard data
```

### Email Provider

```bash
# Set EMAIL_PROVIDER=console and check logs for:
# "CONSOLE EMAIL PROVIDER (Development Mode)"
```

---

## Monitoring Queries

### Daily Email Stats

```sql
SELECT DATE(sent_at), email_type, status, COUNT(*)
FROM email_send_logs
WHERE sent_at > NOW() - INTERVAL '7 days'
GROUP BY DATE(sent_at), email_type, status
ORDER BY DATE(sent_at) DESC;
```

### Active Users (Last 7 Days)

```sql
SELECT COUNT(DISTINCT parent_email) as active_parents,
       COUNT(*) as total_sessions
FROM hint_sessions
WHERE started_at > NOW() - INTERVAL '7 days'
  AND parent_email IS NOT NULL;
```

### Unsubscribe Rate

```sql
SELECT
  COUNT(*) FILTER (WHERE NOT weekly_digest_enabled) as weekly_unsub,
  COUNT(*) FILTER (WHERE NOT session_reports_enabled) as session_unsub,
  COUNT(*) as total
FROM email_preferences;
```
