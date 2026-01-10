# Manual QA Checklist

> Comprehensive manual testing checklist for StepWise beta release

---

## Overview

This checklist covers the full user journey from landing → problem solving → parent email → unsubscribe → database verification → error tracking. Based on UAT (User Acceptance Testing) and manual testing best practices.

**Test Environment**:

- Local: `http://localhost:3000` (frontend) + `http://localhost:8000` (backend)
- Staging: TBD (Fly.io review app)
- Production: TBD

**Prerequisites**:

- [ ] Backend running (`uvicorn backend.main:app --reload`)
- [ ] Frontend running (`npm run dev`)
- [ ] PostgreSQL running (`docker-compose --profile postgres up -d`)
- [ ] Demo data seeded (`python scripts/seed_demo_data.py`)
- [ ] Beta code available (from `beta_codes_*.csv`)

---

## 1. User Registration & Onboarding

### 1.1 Beta Code Entry

- [ ] Navigate to `http://localhost:3000`
- [ ] See beta code entry screen
- [ ] Enter invalid code → See error message
- [ ] Enter valid code (from CSV) → Proceed to grade selection
- [ ] **Screenshot**: Beta code entry screen

### 1.2 Grade Selection

- [ ] See grade selection screen (Grades 4-9)
- [ ] Select Grade 7 → Proceed to problem entry
- [ ] **Verify**: Grade stored in session/localStorage

### 1.3 First-time User Experience

- [ ] See welcome message or tutorial (if implemented)
- [ ] Understand how to enter a problem
- [ ] Understand hint progression (Concept → Strategy → Step)

---

## 2. Problem Submission & Hint Flow

### 2.1 Problem Entry

- [ ] Enter simple problem: "Solve 2x + 5 = 11"
- [ ] Click "Get Help" or equivalent button
- [ ] **Verify**: Problem accepted, session created
- [ ] **Screenshot**: Problem entry screen

### 2.2 Concept Hint (Layer 1)

- [ ] Receive concept hint (e.g., "This is a linear equation...")
- [ ] Hint does NOT contain the answer
- [ ] Hint is encouraging (no "wrong" or "incorrect" language)
- [ ] **Response Options**: "I understand" / "I'm confused"

### 2.3 Understanding Response - Understood

- [ ] Click "I understand"
- [ ] Proceed to Strategy hint (Layer 2)
- [ ] **Verify**: Response logged with `UNDERSTOOD` status

### 2.4 Understanding Response - Confused

- [ ] Go back and click "I'm confused"
- [ ] Receive clarifying hint or same hint rephrased
- [ ] After 3 confusions, hint becomes more detailed
- [ ] **Verify**: `confusion_count` increments in database

### 2.5 Strategy Hint (Layer 2)

- [ ] Receive strategy hint (e.g., "Isolate x by subtracting 5...")
- [ ] Hint guides approach, doesn't give answer
- [ ] **Response Options**: "I understand" / "I'm confused"

### 2.6 Step-by-Step Hint (Layer 3)

- [ ] Receive step-by-step hint (e.g., "Step 1: Subtract 5 from both sides...")
- [ ] Hint breaks down solution into steps
- [ ] Still doesn't give final answer directly
- [ ] **Response Options**: "I understand" / "I'm confused" / "Reveal Solution"

### 2.7 Reveal Solution

- [ ] Click "Reveal Solution"
- [ ] See full solution with explanation
- [ ] **Verify**: `reveal_count` increments in database
- [ ] **Verify**: Session marked as completed

### 2.8 Session Completion

- [ ] See session summary (time spent, hints used, etc.)
- [ ] Option to enter parent email for report
- [ ] Option to try another problem

---

## 3. Parent Email Flow

### 3.1 Email Entry

- [ ] Enter parent email: `test@example.com`
- [ ] Click "Send Report"
- [ ] See confirmation message
- [ ] **Verify**: Email sent (check console logs in development)

### 3.2 Session Report Email

- [ ] Check email inbox (or console logs)
- [ ] Verify email received with subject "Your child's learning report – StepWise"
- [ ] **Email Content**:
  - [ ] Headline summarizes performance
  - [ ] Performance badge (Excellent/Good/Needs Practice)
  - [ ] Key insights (3-5 bullet points)
  - [ ] Recommendation for next steps
  - [ ] PDF attachment with detailed report
- [ ] **Screenshot**: Email in inbox

### 3.3 Email Headers (RFC 8058)

- [ ] View email source/headers
- [ ] Verify `List-Unsubscribe` header present
- [ ] Verify `List-Unsubscribe-Post` header present
- [ ] **Example**:
  ```
  List-Unsubscribe: <https://yourapp.com/api/v1/email/unsubscribe/{token}?type=session_reports>
  List-Unsubscribe-Post: List-Unsubscribe=One-Click
  ```

### 3.4 Email Footer

- [ ] Verify footer contains:
  - [ ] "Manage email preferences" link
  - [ ] "Unsubscribe from session reports" link
  - [ ] Disclaimer about weekly digests
  - [ ] Support email address
- [ ] **Screenshot**: Email footer

---

## 4. One-Click Unsubscribe Flow

### 4.1 Unsubscribe via Email Client

- [ ] Click "Unsubscribe" button in email client (Gmail, Yahoo, etc.)
- [ ] **Verify**: Unsubscribe processed (check database)
- [ ] **Verify**: No confirmation page shown (one-click)

### 4.2 Unsubscribe via Footer Link

- [ ] Click "Unsubscribe from session reports" link in email footer
- [ ] Redirected to unsubscribe confirmation page
- [ ] See message: "You've been unsubscribed from session reports"
- [ ] **Verify**: `session_reports_enabled = false` in database

### 4.3 Manage Preferences

- [ ] Click "Manage email preferences" link
- [ ] See preference center with toggles:
  - [ ] Session reports (on/off)
  - [ ] Weekly digests (on/off)
- [ ] Toggle session reports off → Save
- [ ] **Verify**: Preference updated in database

### 4.4 Verify Suppression

- [ ] Complete another session with same email
- [ ] **Verify**: No email sent (suppressed due to unsubscribe)
- [ ] **Verify**: Log message: "Email suppressed: session reports disabled for {email}"

---

## 5. Database Verification

### 5.1 Problem Table

- [ ] Connect to database: `psql -U stepwise_user -d stepwise_db`
- [ ] Query: `SELECT * FROM problems ORDER BY created_at DESC LIMIT 5;`
- [ ] **Verify**:
  - [ ] `raw_text` contains problem text
  - [ ] `grade_level` matches selected grade
  - [ ] `created_at` timestamp is recent

### 5.2 HintSession Table

- [ ] Query: `SELECT * FROM hint_sessions ORDER BY created_at DESC LIMIT 5;`
- [ ] **Verify**:
  - [ ] `id` is auto-generated UUID
  - [ ] `problem_id` references correct problem
  - [ ] `current_layer` progresses (CONCEPT → STRATEGY → STEP)
  - [ ] `confusion_count` increments on "I'm confused"
  - [ ] `reveal_count` increments on "Reveal Solution"
  - [ ] `completed_at` timestamp set when session ends

### 5.3 StudentResponse Table

- [ ] Query: `SELECT * FROM student_responses ORDER BY created_at DESC LIMIT 5;`
- [ ] **Verify**:
  - [ ] `session_id` references correct session
  - [ ] `char_count` matches response length
  - [ ] `keywords_matched` contains relevant keywords
  - [ ] `understanding_level` is UNDERSTOOD or CONFUSED

### 5.4 EmailPreferences Table

- [ ] Query: `SELECT * FROM email_preferences WHERE email = 'test@example.com';`
- [ ] **Verify**:
  - [ ] `unsubscribe_token` is UUID
  - [ ] `session_reports_enabled` reflects preference
  - [ ] `weekly_digest_enabled` reflects preference
  - [ ] `created_at` and `updated_at` timestamps

### 5.5 EmailSendLog Table

- [ ] Query: `SELECT * FROM email_send_log ORDER BY created_at DESC LIMIT 5;`
- [ ] **Verify**:
  - [ ] `email` matches recipient
  - [ ] `email_type` is SESSION_REPORT or WEEKLY_DIGEST
  - [ ] `status` is SENT or FAILED
  - [ ] `sent_at` timestamp is recent
  - [ ] `idempotency_key` prevents duplicates

### 5.6 FeedbackItem Table

- [ ] Query: `SELECT * FROM feedback_items ORDER BY created_at DESC LIMIT 5;`
- [ ] **Verify**:
  - [ ] `session_id` references correct session (if applicable)
  - [ ] `locale` is en-US
  - [ ] `grade_level` matches user's grade
  - [ ] `pmf_answer`, `would_pay`, `what_worked`, `what_confused` contain feedback

---

## 6. Sentry Error Tracking

### 6.1 Trigger Test Error

- [ ] Navigate to `http://localhost:3000/test-error` (if route exists)
- [ ] OR: Manually trigger error in code (e.g., `throw new Error("Test error")`)
- [ ] **Verify**: Error appears in browser console

### 6.2 Verify Sentry Capture

- [ ] Log in to Sentry dashboard
- [ ] Navigate to StepWise project
- [ ] **Verify**: Error event captured with:
  - [ ] Error message
  - [ ] Stack trace
  - [ ] User context (if available)
  - [ ] Breadcrumbs (user actions leading to error)
- [ ] **Screenshot**: Sentry error event

### 6.3 Source Maps

- [ ] **Verify**: Stack trace shows original TypeScript/Python code (not minified)
- [ ] **Verify**: File names and line numbers are accurate
- [ ] **Note**: Requires source maps uploaded via `.github/workflows/sentry_sourcemaps.yml`

---

## 7. Performance Testing

### 7.1 Page Load Times

- [ ] Open browser DevTools → Network tab
- [ ] Navigate to `http://localhost:3000`
- [ ] **Verify**: Initial page load < 3s
- [ ] **Verify**: Time to Interactive (TTI) < 5s

### 7.2 Hint Generation Speed

- [ ] Submit problem
- [ ] Measure time from "Get Help" click to hint display
- [ ] **Verify**: Hint generation < 2s
- [ ] **Note**: May be slower on first request (cold start)

### 7.3 API Response Times

- [ ] Open browser DevTools → Network tab
- [ ] Submit problem → Check `/api/v1/sessions/start` request
- [ ] **Verify**: Response time < 500ms
- [ ] Respond to hint → Check `/api/v1/sessions/{id}/respond` request
- [ ] **Verify**: Response time < 1s

---

## 8. Accessibility Testing

### 8.1 Keyboard Navigation

- [ ] Navigate entire app using only keyboard (Tab, Enter, Esc)
- [ ] **Verify**: All interactive elements reachable
- [ ] **Verify**: Focus indicators visible
- [ ] **Verify**: Logical tab order

### 8.2 Screen Reader Compatibility

- [ ] Enable screen reader (VoiceOver on macOS, NVDA on Windows)
- [ ] Navigate app with screen reader
- [ ] **Verify**: All content announced correctly
- [ ] **Verify**: Form labels associated with inputs
- [ ] **Verify**: Error messages announced

### 8.3 Color Contrast

- [ ] Use browser extension (e.g., axe DevTools)
- [ ] **Verify**: All text meets WCAG AA contrast ratio (4.5:1 for normal text)
- [ ] **Verify**: Interactive elements meet contrast requirements

### 8.4 Responsive Design

- [ ] Test on mobile viewport (375px width)
- [ ] Test on tablet viewport (768px width)
- [ ] Test on desktop viewport (1920px width)
- [ ] **Verify**: Layout adapts appropriately
- [ ] **Verify**: No horizontal scrolling
- [ ] **Verify**: Touch targets ≥ 44x44px on mobile

---

## 9. Security Testing

### 9.1 API Key Protection

- [ ] View page source
- [ ] **Verify**: No API keys exposed in frontend code
- [ ] **Verify**: OpenAI API key only in backend environment variables

### 9.2 HTTPS Enforcement

- [ ] **Production Only**: Navigate to `http://yourapp.com`
- [ ] **Verify**: Redirects to `https://yourapp.com`
- [ ] **Verify**: SSL certificate valid

### 9.3 CORS Configuration

- [ ] Open browser DevTools → Console
- [ ] **Verify**: No CORS errors when making API requests
- [ ] **Verify**: CORS headers allow only trusted origins

### 9.4 Input Validation

- [ ] Submit problem with SQL injection attempt: `'; DROP TABLE problems; --`
- [ ] **Verify**: Input sanitized, no SQL injection
- [ ] Submit problem with XSS attempt: `<script>alert('XSS')</script>`
- [ ] **Verify**: Input escaped, no script execution

---

## 10. Reliability Testing

### 10.1 30-Minute Session

- [ ] Use app continuously for 30 minutes
- [ ] Complete 5-10 problems
- [ ] **Verify**: No crashes or freezes
- [ ] **Verify**: No memory leaks (check browser Task Manager)

### 10.2 Network Interruption

- [ ] Disable network mid-session
- [ ] **Verify**: Graceful error message (not blank screen)
- [ ] Re-enable network
- [ ] **Verify**: App recovers, session state preserved

### 10.3 Concurrent Sessions

- [ ] Open app in 3 different browser tabs
- [ ] Complete different problems in each tab
- [ ] **Verify**: Sessions don't interfere with each other
- [ ] **Verify**: All sessions saved correctly in database

---

## 11. UAT Elements

### 11.1 Usability

- [ ] **Test**: Can a parent navigate the app without instructions?
- [ ] **Test**: Can a student understand hint progression without help?
- [ ] **Test**: Is the unsubscribe process obvious and easy?

### 11.2 Learnability

- [ ] **Test**: How long does it take a new user to complete their first problem?
- [ ] **Target**: < 5 minutes from landing to first hint

### 11.3 Efficiency

- [ ] **Test**: How many clicks to complete a problem?
- [ ] **Target**: ≤ 10 clicks (enter problem → get hints → complete)

### 11.4 Error Prevention

- [ ] **Test**: Are destructive actions (e.g., delete session) confirmed?
- [ ] **Test**: Are error messages helpful and actionable?

### 11.5 Satisfaction

- [ ] **Test**: Would you recommend this app to a friend? (1-10 scale)
- [ ] **Target**: ≥ 8/10 average score

---

## 12. Edge Cases & Error Scenarios

### 12.1 Empty Problem Submission

- [ ] Submit empty problem text
- [ ] **Verify**: Error message: "Please enter a math problem"

### 12.2 Invalid Email Format

- [ ] Enter invalid email: `notanemail`
- [ ] **Verify**: Error message: "Please enter a valid email address"

### 12.3 Duplicate Email Send

- [ ] Complete session, send email
- [ ] Immediately complete another session with same email
- [ ] **Verify**: Second email sent (no idempotency issue)
- [ ] **Verify**: Both emails logged in `email_send_log`

### 12.4 Unsubscribe Token Expiry

- [ ] **Manual Test**: Set `unsubscribe_token` expiry in past
- [ ] Click unsubscribe link
- [ ] **Verify**: Error message: "This unsubscribe link has expired"

### 12.5 Database Connection Failure

- [ ] Stop PostgreSQL: `docker-compose stop postgres`
- [ ] Try to submit problem
- [ ] **Verify**: Graceful error message (not 500 Internal Server Error)
- [ ] **Verify**: Error logged to Sentry

---

## 13. Regression Testing

### 13.1 Previous Bug Fixes

- [ ] **Test**: All bugs fixed in previous releases still fixed
- [ ] **Reference**: GitHub Issues with `bug` label

### 13.2 Core Functionality

- [ ] **Test**: Problem submission still works after new features added
- [ ] **Test**: Email delivery still works after new features added
- [ ] **Test**: Unsubscribe still works after new features added

---

## 14. Automated E2E Testing ✅

### 14.1 Run Playwright E2E Tests

- [x] **Status**: Completed (2026-01-10 14:15 EST)
- [x] **Test Suite**: Playwright E2E tests
- [x] **Result**: 76/77 tests passing (98.7%)
- [x] **Overall QA**: 404/405 tests passing (99.75%)

### 14.2 Test Execution Commands

**Run all E2E tests**:

```bash
cd frontend
npx playwright test
```

**Run with specific browser**:

```bash
npx playwright test --project=chromium
```

**Run with list reporter**:

```bash
npx playwright test --reporter=list
```

**Run specific test file**:

```bash
npx playwright test tests/e2e/hint-flow.spec.ts
```

**Run with browser UI (headed mode)**:

```bash
npx playwright test --headed
```

**Debug mode**:

```bash
npx playwright test --debug
```

**View HTML report**:

```bash
npx playwright show-report
```

### 14.3 Test Results Summary (2026-01-10)

**Backend Tests**: ✅ 328/328 passing (100%)

- Unit tests: All passing
- Contract tests: All passing
- Execution time: 5.99s

**Frontend E2E Tests**: ⚠️ 76/77 passing (98.7%)

- Beta Gate: 11/11 passing ✅
- Email Reports: 8/8 passing ✅
- Feedback: 5/5 passing ✅
- Feedback Dashboard: 5/5 passing ✅
- Hint Flow: 25/26 passing ⚠️ (1 failure in Reveal Solution)
- Onboarding: 18/18 passing ✅
- PDF Report: 3/3 passing ✅
- Execution time: 9.9s

**Overall QA Status**: ✅ 404/405 tests passing (99.75%)

### 14.4 Known Issue

**Failed Test**: `tests/e2e/hint-flow.spec.ts:294`

- **Test Name**: "Reveal Solution Flow › clicking reveal shows solution viewer"
- **Issue**: GitHub #10
- **Severity**: Low (non-critical, solution reveal feature)
- **Impact**: Does not block beta launch
- **Planned Fix**: Post-beta (v0.2.0)

### 14.5 Test Artifacts

- **Screenshots**: `test-results/**/*.png`
- **Error Context**: `test-results/**/error-context.md`
- **HTML Report**: Run `npx playwright show-report` to view

### 14.6 Playwright CLI Reference

For more Playwright commands, see:

- [Playwright Test CLI](https://playwright.dev/docs/test-cli)
- [Playwright Test Reporters](https://playwright.dev/docs/test-reporters)
- [Playwright Test Debugging](https://playwright.dev/docs/debug)

---

## Sign-off

**Tester Name**: \***\*\*\*\*\*\*\***\_\_\_\***\*\*\*\*\*\*\***

**Date**: \***\*\*\*\*\*\*\***\_\_\_\***\*\*\*\*\*\*\***

**Environment**: [ ] Local [ ] Staging [ ] Production

**Overall Status**: [ ] Pass [ ] Fail [ ] Pass with Issues

**Critical Issues Found**: \***\*\*\*\*\*\*\***\_\_\_\***\*\*\*\*\*\*\***

**Notes**: \***\*\*\*\*\*\*\***\_\_\_\***\*\*\*\*\*\*\***

---

## References

- [UAT Best Practices](https://www.softwaretestinghelp.com/user-acceptance-testing-uat/)
- [Manual Testing Checklist](https://www.guru99.com/manual-testing.html)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
