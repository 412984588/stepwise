# Security Posture - StepWise Backend

**Last Updated**: 2026-01-08
**Status**: Production Hardening in Progress

This document describes the security mitigations implemented for production deployment.

---

## Overview

StepWise implements layered security controls focused on:

1. **Email Idempotency** - Preventing duplicate emails from retries
2. **Email Suppression** - Enforcing unsubscribe preferences at send time
3. **Abuse Prevention** - Per-email throttling to prevent cost amplification
4. **Token-Based Access** - Session tokens for user endpoints (not API keys in browser)
5. **Audit Trail** - Complete logging of email sends and throttling events

---

## 1. Email Idempotency & Deduplication

### Problem

- Session completion endpoint may be called multiple times (retries, double-clicks)
- Weekly digest script may run multiple times in same week (cron failures, manual reruns)
- Without idempotency, users receive duplicate emails

### Solution: EmailSendLog Table

```sql
CREATE TABLE email_send_logs (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    email_type VARCHAR(50) NOT NULL,  -- 'session_report' or 'weekly_digest'
    session_id VARCHAR(36),            -- For session reports
    week_start_date DATE,              -- For weekly digests
    idempotency_key VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- 'pending', 'sent', 'failed'
    error_message VARCHAR(500),
    sent_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL,

    -- Idempotency constraints
    CONSTRAINT uq_email_session_report UNIQUE (email, email_type, session_id)
        WHERE email_type='session_report' AND status='sent',
    CONSTRAINT uq_email_weekly_digest UNIQUE (email, email_type, week_start_date)
        WHERE email_type='weekly_digest' AND status='sent'
);
```

### Idempotency Rules

**Session Reports**:

- **Key**: `session_report:{email}:{session_id}`
- **Constraint**: At most ONE successful send per (email, session_id)
- **Behavior**: Second completion for same session + email → returns success but doesn't send

**Weekly Digests**:

- **Key**: `weekly_digest:{email}:{week_start_date}`
- **Constraint**: At most ONE successful send per (email, week)
- **Behavior**: Running script twice in same week → second run skips all emails already sent

### Send Flow

```python
def send_email_with_idempotency(email, email_type, ...):
    # 1. Generate idempotency key
    key = generate_idempotency_key(email, email_type, session_id, week_start)

    # 2. Check if already sent
    existing = db.query(EmailSendLog).filter_by(
        idempotency_key=key,
        status='sent'
    ).first()

    if existing:
        return True  # Already sent, idempotent success

    # 3. Create pending log entry
    log = EmailSendLog(
        email=email,
        idempotency_key=key,
        status='pending',
        ...
    )
    db.add(log)
    db.commit()

    # 4. Attempt send
    try:
        success = provider.send_email(message)
        if success:
            log.status = 'sent'
            log.sent_at = utc_now()
        else:
            log.status = 'failed'
            log.error_message = "Provider returned false"
    except Exception as e:
        log.status = 'failed'
        log.error_message = str(e)[:500]

    db.commit()
    return log.status == 'sent'
```

### Retry Behavior

- **SENT**: Returns success immediately, no retry
- **FAILED**: Allows retry after exponential backoff (optional)
- **PENDING**: Considered stale after 10 minutes, allows retry

---

## 2. Email Preference Enforcement

### Problem

- Unsubscribe only worked at script level (weekly digests)
- If code bypassed preference check, email still sent
- No unified preference management for different email types

### Solution: Unified EmailPreference Model

```python
class EmailPreference:
    email: str
    session_reports_enabled: bool = True
    weekly_digest_enabled: bool = True
    unsubscribe_token: str
    updated_at: datetime
```

### Enforcement Point: Email Service

**ALL email sends MUST check preferences**:

```python
def send_email(self, email, email_type, ...):
    # 1. Check preference FIRST (suppression at send time)
    if email_type == EmailType.SESSION_REPORT:
        if not EmailPreferenceService.is_session_reports_enabled(db, email):
            logger.info(f"Suppressed: session report disabled for {email}")
            return True  # Return success to avoid errors

    elif email_type == EmailType.WEEKLY_DIGEST:
        if not EmailPreferenceService.is_weekly_digest_enabled(db, email):
            logger.info(f"Suppressed: weekly digest disabled for {email}")
            return True

    # 2. Continue with idempotency check...
    # 3. Continue with throttle check...
    # 4. Actually send if all checks pass
```

### Unsubscribe Page Enhancement

```
Original: "Unsubscribe from weekly reports"
Enhanced:
  - "You are unsubscribed from weekly learning reports"
  - "Click here to also unsubscribe from session completion emails"
  - Both use same token but different actions
```

---

## 3. Abuse Prevention & Throttling

### Problem

- Without authentication, anyone can trigger expensive operations
- Email sending has cost (SendGrid, AWS SES)
- PDF generation is CPU-intensive
- IP-based rate limiting fails with rotating IPs / VPNs

### Solution: Per-Email DB-Based Throttling

```sql
CREATE TABLE email_throttles (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    email_type VARCHAR(50) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    send_count INTEGER NOT NULL DEFAULT 1,
    last_send_at TIMESTAMP NOT NULL,

    INDEX idx_email_type_window (email, email_type, window_start)
);
```

### Throttle Limits

| Resource                | Limit | Window   | Scope             |
| ----------------------- | ----- | -------- | ----------------- |
| Session report emails   | 5     | 24 hours | Per email address |
| Weekly digest emails    | 1     | 7 days   | Per email address |
| PDF generation          | 20    | 1 hour   | Per session_id    |
| Stats/dashboard queries | 100   | 1 hour   | Per session_id    |

### Throttle Check Logic

```python
def check_throttle(email, email_type):
    window_start = get_current_window_start(email_type)  # e.g., today 00:00 UTC

    throttle = db.query(EmailThrottle).filter_by(
        email=email,
        email_type=email_type,
        window_start=window_start
    ).first()

    if not throttle:
        # First send in this window
        throttle = EmailThrottle(
            email=email,
            email_type=email_type,
            window_start=window_start,
            send_count=1
        )
        db.add(throttle)
        db.commit()
        return True, get_limit(email_type)

    limit = get_limit(email_type)
    if throttle.send_count >= limit:
        # Rate limit exceeded
        return False, 0

    # Increment count
    throttle.send_count += 1
    throttle.last_send_at = utc_now()
    db.commit()

    remaining = limit - throttle.send_count
    return True, remaining
```

### Error Responses

```json
// Rate limit exceeded (429)
{
    "error": "RATE_LIMIT_EXCEEDED",
    "message": "Too many session reports. Please try again in 24 hours.",
    "retry_after": 86400
}

// Cost limit exceeded (402)
{
    "error": "QUOTA_EXCEEDED",
    "message": "PDF generation limit reached for this session. Upgrade for unlimited access.",
    "limit": 20,
    "window": "1 hour"
}
```

---

## 4. Token-Based Access Control

### Problem

- X-API-Key in browser leaks to all users
- Anyone with API key can access all sessions
- Need session-level access control without full auth

### Solution: Session Access Tokens

**Implementation**:

```python
class HintSession:
    session_access_token: str  # UUID v4, generated at session start
```

**Token Generation** (at session start):

```python
POST /api/v1/sessions/start
{
    "problem_text": "2x + 5 = 11"
}

Response:
{
    "session_id": "abc-123",
    "session_access_token": "def-456",  # NEW
    "hint": {...}
}
```

**Token Usage** (protected endpoints):

```python
# Frontend stores session_access_token with session_id
# All subsequent requests include it

GET /api/v1/reports/{session_id}/pdf
Headers:
    X-Session-Access-Token: def-456

GET /api/v1/stats/summary?session_id=abc-123
Headers:
    X-Session-Access-Token: def-456
```

**Validation**:

```python
def validate_session_access(session_id: str, token: str) -> bool:
    session = db.query(HintSession).filter_by(id=session_id).first()

    if not session:
        raise HTTPException(404, "Session not found")

    if session.session_access_token != token:
        raise HTTPException(403, "Invalid session access token")

    return True
```

### Token Rotation

- **Per-session**: Each session gets a new token
- **No expiration**: Token valid for session lifetime
- **No refresh**: No refresh tokens (sessions are short-lived)

### API Key Usage (Server-Only)

**Keep for**:

- Admin endpoints (future)
- Server-to-server integration (future)
- Operational monitoring (stats aggregation)

**Remove from**:

- Frontend user flows
- Session-specific operations
- PDF/report downloads

---

## 5. Email Validation & Consent

### Email Format Validation (Server-Side)

```python
import re

EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

def validate_email(email: str) -> bool:
    if not email or len(email) > 255:
        return False

    if not EMAIL_REGEX.match(email):
        return False

    # Additional checks
    if email.count('@') != 1:
        return False

    local, domain = email.split('@')
    if len(local) > 64 or len(domain) > 255:
        return False

    return True
```

### Consent Linkage

**Rule**: Session report can only be sent if:

1. Email provided in session completion request
2. Email stored in `parent_email` field on session
3. Email passes format validation

**Enforcement**:

```python
def send_session_report(session_id, requested_email):
    session = get_session(session_id)

    # Consent check: email must match what was provided at completion
    if not session.parent_email:
        raise ValueError("No parent email on session")

    if session.parent_email != requested_email:
        raise ValueError("Email mismatch - consent violation")

    # Proceed with send...
```

---

## 6. Operational Considerations

### Cron Job Idempotency

**Weekly Digest Script**:

```bash
# Safe to run multiple times - idempotent by design
0 9 * * 1 cd /app && python scripts/send_weekly_digests.py

# If cron fails and retries, EmailSendLog prevents duplicates
# If admin manually reruns, same - no duplicates
```

**Monitoring Commands**:

```bash
# Check sends in last 24h
SELECT email_type, status, COUNT(*)
FROM email_send_logs
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY email_type, status;

# Check throttle violations
SELECT email, email_type, send_count, window_start
FROM email_throttles
WHERE send_count >= 5  -- Adjust based on limits
ORDER BY send_count DESC;

# Find emails with send failures
SELECT email, email_type, error_message, COUNT(*)
FROM email_send_logs
WHERE status = 'failed'
GROUP BY email, email_type, error_message
ORDER BY COUNT(*) DESC;
```

### Database Cleanup

**EmailSendLog retention**:

- Keep 90 days for audit trail
- Archive older records to cold storage

```sql
-- Cleanup job (run monthly)
DELETE FROM email_send_logs
WHERE created_at < NOW() - INTERVAL '90 days'
AND status = 'sent';

-- Keep failures longer for debugging
DELETE FROM email_send_logs
WHERE created_at < NOW() - INTERVAL '180 days'
AND status = 'failed';
```

**EmailThrottle cleanup**:

- Delete windows older than 7 days

```sql
-- Cleanup job (run daily)
DELETE FROM email_throttles
WHERE window_start < NOW() - INTERVAL '7 days';
```

---

## 7. Testing Strategy

### Idempotency Tests

```python
def test_session_report_idempotent():
    # Complete session with email
    complete_session(session_id, email="parent@example.com")

    # Complete again (retry/double-click)
    complete_session(session_id, email="parent@example.com")

    # Verify only ONE email sent
    logs = db.query(EmailSendLog).filter_by(
        session_id=session_id,
        status='sent'
    ).all()

    assert len(logs) == 1

def test_weekly_digest_idempotent():
    # Run digest script
    send_weekly_digests(days=7)

    # Run again immediately
    send_weekly_digests(days=7)

    # Verify no duplicates sent
    logs = db.query(EmailSendLog).filter_by(
        email_type='weekly_digest',
        week_start_date=get_week_start(),
        status='sent'
    ).all()

    # One email per unique email address
    assert len(logs) == len(set(log.email for log in logs))
```

### Throttle Tests

```python
def test_session_report_throttle():
    email = "parent@example.com"

    # Send 5 reports (at limit)
    for i in range(5):
        send_session_report(f"session-{i}", email)

    # 6th should be throttled
    with pytest.raises(HTTPException) as exc:
        send_session_report("session-6", email)

    assert exc.value.status_code == 429
    assert "RATE_LIMIT_EXCEEDED" in str(exc.value.detail)
```

### Token Tests

```python
def test_session_access_token_required():
    # Start session
    response = start_session("2x + 5 = 11")
    session_id = response['session_id']
    token = response['session_access_token']

    # Valid token works
    pdf = get_pdf_report(session_id, headers={"X-Session-Access-Token": token})
    assert pdf is not None

    # Missing token fails
    with pytest.raises(HTTPException) as exc:
        get_pdf_report(session_id)
    assert exc.value.status_code == 403

    # Invalid token fails
    with pytest.raises(HTTPException) as exc:
        get_pdf_report(session_id, headers={"X-Session-Access-Token": "wrong"})
    assert exc.value.status_code == 403
```

---

## 8. Production Deployment Checklist

- [ ] Review all throttle limits and adjust for production scale
- [ ] Set up EmailSendLog cleanup cron job (monthly)
- [ ] Set up EmailThrottle cleanup cron job (daily)
- [ ] Configure monitoring alerts for:
  - [ ] High email send failure rate (>5%)
  - [ ] Throttle violations spike (>100/hour)
  - [ ] Duplicate send attempts (should be 0 with idempotency)
- [ ] Test weekly digest script idempotency in staging
- [ ] Verify session_access_token generation at session start
- [ ] Update frontend to store and send session_access_token
- [ ] Remove X-API-Key from frontend code
- [ ] Document re-subscribe process for support team
- [ ] Train support team on throttle limit exceptions
- [ ] Set up audit log review process (weekly)

---

## 9. Known Limitations & Future Work

**Current MVP Constraints**:

- No user accounts (email-based only)
- No per-user quota management
- No IP-based rate limiting (relies on email throttling)
- No CAPTCHA or proof-of-work for abuse prevention
- No email verification (accepts any valid format)

**Future Enhancements**:

- Email verification flow (verify ownership before first send)
- User accounts with session history
- Graduated throttle limits based on user tier
- Machine learning-based abuse detection
- Webhook notifications for throttle violations
- Admin dashboard for throttle management
- Bulk preference management API

---

## 10. Security Contacts

**Report Security Issues**:

- Email: security@stepwise.example.com
- Response Time: 24 hours
- Disclosure Policy: 90-day coordinated disclosure

**Operational Issues**:

- Email throttle exceptions: support@stepwise.example.com
- Email delivery problems: support@stepwise.example.com
- Unsubscribe assistance: support@stepwise.example.com
