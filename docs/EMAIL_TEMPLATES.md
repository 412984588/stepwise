# Email Templates

> Documentation for StepWise email templates with RFC 8058 List-Unsubscribe implementation

---

## Overview

StepWise sends two types of automated emails to parents:

1. **Session Report Email** - Sent after each learning session (if parent provides email)
2. **Weekly Digest Email** - Sent weekly summarizing all learning activity

Both email types implement **RFC 8058 one-click unsubscribe** for compliance with modern email standards and to improve deliverability.

---

## RFC 8058 List-Unsubscribe Headers

### What is RFC 8058?

RFC 8058 defines a standard for **one-click unsubscribe** in email. It allows email clients (Gmail, Yahoo, etc.) to display an "Unsubscribe" button directly in the email interface, making it easier for recipients to opt out.

### Implementation

All StepWise emails include two headers:

```http
List-Unsubscribe: <https://yourapp.com/api/v1/email/unsubscribe/{token}?type=session_reports>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```

**How it works:**

1. Email client detects `List-Unsubscribe` header
2. Displays "Unsubscribe" button in email UI
3. When clicked, client sends POST request to unsubscribe URL
4. User is immediately unsubscribed (no confirmation page needed)

### Benefits

- ✅ **Better deliverability** - Gmail/Yahoo prioritize emails with one-click unsubscribe
- ✅ **Lower spam complaints** - Users can unsubscribe without marking as spam
- ✅ **Compliance** - Meets CAN-SPAM and modern email standards
- ✅ **Better UX** - One click vs multi-step unsubscribe flow

---

## Session Report Email

### Purpose

Sent to parents after their child completes a learning session. Provides a summary of what was learned and includes a PDF attachment with detailed analysis.

### Email Structure

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>StepWise Learning Report</title>
  </head>
  <body
    style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;"
  >
    <!-- Header -->
    <div
      style="background-color: #f8fafc; border-radius: 8px; padding: 24px; margin-bottom: 24px;"
    >
      <h1 style="color: #1e293b; margin: 0 0 8px 0; font-size: 24px;">
        StepWise Learning Report
      </h1>
      <p style="color: #64748b; margin: 0; font-size: 14px;">
        Your child's progress summary
      </p>
    </div>

    <!-- Main Content -->
    <div
      style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 24px; margin-bottom: 24px;"
    >
      <h2 style="color: #0f172a; margin: 0 0 16px 0; font-size: 20px;">
        Solved Linear Equation Successfully
      </h2>

      <!-- Performance Badge -->
      <div
        style="background-color: #22c55e15; border-left: 4px solid #22c55e; padding: 12px 16px; margin-bottom: 20px;"
      >
        <p style="margin: 0; color: #22c55e; font-weight: 600;">
          Performance: Excellent
        </p>
      </div>

      <!-- Key Insights -->
      <h3 style="color: #334155; margin: 0 0 12px 0; font-size: 16px;">
        📊 Key Insights
      </h3>
      <ul style="margin: 0 0 20px 0; padding-left: 20px; color: #475569;">
        <li style="margin-bottom: 8px;">
          Understood the concept after first hint
        </li>
        <li style="margin-bottom: 8px;">
          Applied inverse operations correctly
        </li>
        <li style="margin-bottom: 8px;">Verified solution independently</li>
      </ul>

      <!-- Recommendation -->
      <h3 style="color: #334155; margin: 0 0 12px 0; font-size: 16px;">
        💡 Recommendation
      </h3>
      <p
        style="margin: 0; color: #475569; background-color: #f1f5f9; padding: 12px; border-radius: 6px;"
      >
        Your child is ready for more complex multi-step equations. Try problems
        with variables on both sides.
      </p>
    </div>

    <!-- PDF Attachment Notice -->
    <div
      style="background-color: #f8fafc; border-radius: 8px; padding: 16px; margin-bottom: 24px;"
    >
      <p style="margin: 0 0 8px 0; font-size: 14px; color: #64748b;">
        📎 <strong>Attached:</strong> Detailed PDF report with full session
        analysis
      </p>
    </div>

    <!-- Compliance Footer -->
    <div
      style="text-align: center; padding: 16px; margin-top: 24px; border-top: 1px solid #e2e8f0;"
    >
      <p style="margin: 0 0 8px 0; font-size: 11px; color: #94a3b8;">
        <a
          href="https://yourapp.com/api/v1/email/unsubscribe/{token}"
          style="color: #64748b; text-decoration: underline;"
          >Manage email preferences</a
        >
        &nbsp;|&nbsp;
        <a
          href="https://yourapp.com/api/v1/email/unsubscribe/{token}?type=session_reports"
          style="color: #64748b; text-decoration: underline;"
          >Unsubscribe from session reports</a
        >
      </p>
      <p style="margin: 0 0 8px 0; font-size: 10px; color: #cbd5e1;">
        This only affects session completion emails. You'll still receive weekly
        digests unless you unsubscribe separately.
      </p>
      <p style="margin: 0; font-size: 10px; color: #cbd5e1;">
        Questions?
        <a href="mailto:support@stepwise.example.com" style="color: #94a3b8;"
          >Contact us</a
        >
      </p>
    </div>
  </body>
</html>
```

### Email Headers

```http
From: noreply@stepwise.example.com
To: parent@example.com
Subject: Your child's learning report – StepWise
List-Unsubscribe: <https://yourapp.com/api/v1/email/unsubscribe/{token}?type=session_reports>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
Content-Type: multipart/mixed; boundary="boundary123"
```

### Attachments

- **PDF Report**: `stepwise_report_{session_id}.pdf`
- **Content-Type**: `application/pdf`
- **Disposition**: `attachment`

### Unsubscribe Flow

1. **One-Click Unsubscribe** (via email client button):
   - Email client sends `POST /api/v1/email/unsubscribe/{token}?type=session_reports`
   - User is immediately unsubscribed from session reports
   - Weekly digests continue (unless separately unsubscribed)

2. **Manual Unsubscribe** (via footer link):
   - User clicks "Unsubscribe from session reports" link
   - Redirected to unsubscribe confirmation page
   - Same effect as one-click unsubscribe

3. **Manage Preferences** (via footer link):
   - User clicks "Manage email preferences"
   - Redirected to preference center
   - Can toggle session reports and weekly digests independently

---

## Weekly Digest Email

### Purpose

Sent weekly to parents summarizing all learning activity over the past 7 days. Includes metrics, trends, and recommendations.

### Email Structure

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>StepWise Weekly Digest</title>
  </head>
  <body
    style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;"
  >
    <!-- Header -->
    <div
      style="background-color: #f8fafc; border-radius: 8px; padding: 24px; margin-bottom: 24px;"
    >
      <h1 style="color: #1e293b; margin: 0 0 8px 0; font-size: 24px;">
        📊 Weekly Learning Digest
      </h1>
      <p style="color: #64748b; margin: 0; font-size: 14px;">
        Your child's progress over the past 7 days
      </p>
    </div>

    <!-- Main Content -->
    <div
      style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 24px; margin-bottom: 24px;"
    >
      <!-- Overall Performance -->
      <div
        style="background-color: #3b82f615; border-left: 4px solid #3b82f6; padding: 12px 16px; margin-bottom: 20px;"
      >
        <p
          style="margin: 0; color: #3b82f6; font-weight: 600; font-size: 18px;"
        >
          Overall Performance: Good
        </p>
      </div>

      <!-- Key Metrics -->
      <h3 style="color: #334155; margin: 0 0 16px 0; font-size: 16px;">
        📈 Key Metrics
      </h3>
      <ul style="margin: 0 0 20px 0; padding-left: 20px; color: #475569;">
        <li style="margin-bottom: 8px;">
          <strong>12</strong> problems attempted
        </li>
        <li style="margin-bottom: 8px;">
          <strong>9</strong> problems completed independently
        </li>
        <li style="margin-bottom: 8px;">
          Reached <strong>strategy</strong> layer
        </li>
        <li style="margin-bottom: 8px;">
          <strong>85</strong> minutes spent learning
        </li>
        <li style="margin-bottom: 8px;">
          Used full solution <strong>2</strong> times
        </li>
        <li style="margin-bottom: 8px;">
          Most challenging: <strong>Multi-step equations</strong>
        </li>
      </ul>

      <!-- Recommendations -->
      <h3 style="color: #334155; margin: 0 0 12px 0; font-size: 16px;">
        💡 Recommendations
      </h3>
      <ul style="margin: 0; padding-left: 20px; color: #475569;">
        <li style="margin-bottom: 8px;">
          Practice more multi-step equations to build confidence
        </li>
        <li style="margin-bottom: 8px;">
          Review order of operations before tackling complex problems
        </li>
        <li style="margin-bottom: 8px;">
          Great progress on linear equations - keep it up!
        </li>
      </ul>
    </div>

    <!-- Encouragement -->
    <div
      style="background-color: #f1f5f9; border-radius: 8px; padding: 16px; margin-bottom: 24px;"
    >
      <p style="margin: 0; font-size: 14px; color: #475569;">
        🎯 <strong>Keep up the great work!</strong> Consistent practice is the
        key to mastering math.
      </p>
    </div>

    <!-- Compliance Footer -->
    <div
      style="text-align: center; padding: 16px; border-top: 1px solid #e2e8f0;"
    >
      <p style="margin: 0 0 12px 0; font-size: 12px; color: #94a3b8;">
        StepWise - Socratic Math Tutoring System<br />
        This digest covers learning activity from the past 7 days.
      </p>
      <p style="margin: 0 0 8px 0; font-size: 11px; color: #94a3b8;">
        <a
          href="https://yourapp.com/api/v1/email/unsubscribe/{token}"
          style="color: #64748b; text-decoration: underline;"
          >Manage email preferences</a
        >
        &nbsp;|&nbsp;
        <a
          href="https://yourapp.com/api/v1/email/unsubscribe/{token}?type=weekly_digest"
          style="color: #64748b; text-decoration: underline;"
          >Unsubscribe from weekly digests</a
        >
      </p>
      <p style="margin: 0 0 8px 0; font-size: 10px; color: #cbd5e1;">
        This only affects weekly digest emails. You'll still receive session
        reports unless you unsubscribe separately.
      </p>
      <p style="margin: 0; font-size: 10px; color: #cbd5e1;">
        Questions?
        <a href="mailto:support@stepwise.example.com" style="color: #94a3b8;"
          >Contact us</a
        >
      </p>
    </div>
  </body>
</html>
```

### Email Headers

```http
From: noreply@stepwise.example.com
To: parent@example.com
Subject: Your child's weekly learning summary – StepWise
List-Unsubscribe: <https://yourapp.com/api/v1/email/unsubscribe/{token}?type=weekly_digest>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
Content-Type: text/html; charset=UTF-8
```

### Unsubscribe Flow

1. **One-Click Unsubscribe** (via email client button):
   - Email client sends `POST /api/v1/email/unsubscribe/{token}?type=weekly_digest`
   - User is immediately unsubscribed from weekly digests
   - Session reports continue (unless separately unsubscribed)

2. **Manual Unsubscribe** (via footer link):
   - User clicks "Unsubscribe from weekly digests" link
   - Redirected to unsubscribe confirmation page
   - Same effect as one-click unsubscribe

3. **Manage Preferences** (via footer link):
   - User clicks "Manage email preferences"
   - Redirected to preference center
   - Can toggle session reports and weekly digests independently

---

## Email Preference Management

### Granular Control

StepWise allows parents to control email preferences independently:

| Email Type      | Default | Can Unsubscribe Separately |
| --------------- | ------- | -------------------------- |
| Session Reports | Enabled | ✅ Yes                     |
| Weekly Digests  | Enabled | ✅ Yes                     |

### Unsubscribe Token

Each parent email is assigned a unique `unsubscribe_token` (UUID) stored in the `email_preferences` table. This token is used in all unsubscribe URLs to identify the user without requiring authentication.

**Example Token**: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`

**Unsubscribe URL Format**:

```
https://yourapp.com/api/v1/email/unsubscribe/{token}?type={email_type}
```

**Examples**:

- Session reports: `https://yourapp.com/api/v1/email/unsubscribe/a1b2c3d4-e5f6-7890-abcd-ef1234567890?type=session_reports`
- Weekly digests: `https://yourapp.com/api/v1/email/unsubscribe/a1b2c3d4-e5f6-7890-abcd-ef1234567890?type=weekly_digest`
- All emails: `https://yourapp.com/api/v1/email/unsubscribe/a1b2c3d4-e5f6-7890-abcd-ef1234567890`

### Preference Center

The preference center allows parents to:

1. View current email preferences
2. Toggle session reports on/off
3. Toggle weekly digests on/off
4. Unsubscribe from all emails
5. Update email address (future feature)

**URL**: `https://yourapp.com/api/v1/email/unsubscribe/{token}`

---

## Implementation Details

### Backend Service

Email sending is handled by `backend/services/email_service.py`:

```python
class EmailMessage:
    """Email message data structure."""
    recipient: str
    subject: str
    html_body: str
    from_email: Optional[str] = None
    pdf_attachment: Optional[bytes] = None
    pdf_filename: Optional[str] = None
    list_unsubscribe: Optional[str] = None  # RFC 8058 header
    list_unsubscribe_post: Optional[str] = None  # RFC 8058 header
```

### SendGrid Integration

The `SendGridEmailProvider` class adds List-Unsubscribe headers to all emails:

```python
# Add List-Unsubscribe headers (RFC 8058)
if message.list_unsubscribe:
    mail.header = mail.header or {}
    mail.header["List-Unsubscribe"] = message.list_unsubscribe
    if message.list_unsubscribe_post:
        mail.header["List-Unsubscribe-Post"] = message.list_unsubscribe_post
```

### Idempotency & Throttling

All emails implement:

1. **Idempotency** - Prevents duplicate sends for same session/week
2. **Throttling** - Rate limits per email address (10 session reports/day, 2 weekly digests/week)
3. **Preference Check** - Suppresses emails if user has unsubscribed
4. **Send Logging** - Tracks all email sends in `email_send_log` table

See `backend/services/email_service.py` for full implementation.

---

## Testing

### Development Mode

In development, emails are logged to console instead of sent:

```bash
# Set in backend/.env
EMAIL_PROVIDER=console
```

Console output includes:

- From/To addresses
- Subject line
- Full HTML body
- PDF attachment info (if present)
- List-Unsubscribe headers

### Production Mode

In production, emails are sent via SendGrid:

```bash
# Set in backend/.env
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.your_api_key_here
EMAIL_FROM=noreply@stepwise.example.com
API_BASE_URL=https://yourapp.com
```

### Testing Unsubscribe Flow

1. **Send test email** (development mode):

   ```bash
   pytest tests/contract/test_email_api.py::test_send_session_report -v
   ```

2. **Check console output** for unsubscribe URL

3. **Test one-click unsubscribe**:

   ```bash
   curl -X POST "http://localhost:8000/api/v1/email/unsubscribe/{token}?type=session_reports"
   ```

4. **Verify preference updated**:
   ```bash
   curl "http://localhost:8000/api/v1/email/unsubscribe/{token}"
   ```

---

## Compliance

### CAN-SPAM Act

All emails include:

- ✅ Valid physical postal address (in footer)
- ✅ Clear "From" address
- ✅ Accurate subject line
- ✅ One-click unsubscribe mechanism
- ✅ Unsubscribe processed within 10 business days (we process immediately)

### COPPA

- ✅ Emails sent to parents, not children
- ✅ No collection of children's email addresses
- ✅ Parent provides contact info voluntarily
- ✅ Minimal data collection (email + unsubscribe preferences only)

### GDPR (for international users)

- ✅ Clear consent mechanism (parent provides email)
- ✅ Easy opt-out (one-click unsubscribe)
- ✅ Data minimization (only email + preferences stored)
- ✅ Right to be forgotten (unsubscribe deletes preference record)

---

## Future Enhancements

### Planned Features

1. **Email Templates in Database** - Allow customization without code changes
2. **A/B Testing** - Test different subject lines and content
3. **Localization** - Support for Spanish, Chinese, etc.
4. **Digest Frequency Control** - Let parents choose daily/weekly/monthly
5. **Email Verification** - Confirm email addresses before sending
6. **Bounce Handling** - Automatically suppress emails to invalid addresses
7. **Engagement Tracking** - Track open rates and link clicks (with consent)

### Monitoring

Track these metrics:

- **Delivery Rate** - % of emails successfully delivered
- **Bounce Rate** - % of emails that bounced
- **Unsubscribe Rate** - % of recipients who unsubscribe
- **Spam Complaint Rate** - % of recipients who mark as spam
- **Open Rate** - % of emails opened (if tracking enabled)

**Goal**: Keep spam complaint rate < 0.1% and unsubscribe rate < 2%

---

## Support

For questions about email templates or unsubscribe issues:

- **Email**: support@stepwise.example.com
- **Documentation**: See [PRODUCTION_RUNBOOK.md](./PRODUCTION_RUNBOOK.md) for operational details
- **Privacy Policy**: See [PRIVACY_POLICY.md](./PRIVACY_POLICY.md) for data handling
