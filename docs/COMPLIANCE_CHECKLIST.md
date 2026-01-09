# Compliance Checklist

> Pre-launch checklist for CAN-SPAM, COPPA, and email deliverability compliance.

## CAN-SPAM Compliance

| Requirement                                | Status | Notes                                         |
| ------------------------------------------ | ------ | --------------------------------------------- |
| **Accurate "From" header**                 | ☐      | Use consistent sender name (e.g., "StepWise") |
| **Non-deceptive subject lines**            | ☐      | Subject must reflect content                  |
| **Physical address in emails**             | ☐      | Add company address to email footer           |
| **Clear unsubscribe mechanism**            | ✅     | One-click unsubscribe link in all emails      |
| **Honor opt-outs within 10 days**          | ✅     | Immediate effect (send-time suppression)      |
| **No selling/sharing email lists**         | ✅     | Policy documented in Privacy Policy           |
| **Identify message as ad (if applicable)** | N/A    | Transactional emails only                     |

### Unsubscribe Requirements

- [x] Single-page unsubscribe (no login required)
- [x] Unsubscribe link in every email
- [x] Clear indication of what is being unsubscribed
- [x] Option to unsubscribe from specific types or all
- [x] Suppression enforced at send time

## COPPA Compliance (Children's Online Privacy Protection Act)

| Requirement                                      | Status | Notes                             |
| ------------------------------------------------ | ------ | --------------------------------- |
| **No personal info collected from children <13** | ✅     | Only anonymous session data       |
| **Parental consent for collection**              | ✅     | Parent provides email for reports |
| **No behavioral advertising to children**        | ✅     | No ads in product                 |
| **No social features**                           | ✅     | No chat, profiles, or messaging   |
| **Clear privacy policy**                         | ☐      | Publish PRIVACY_POLICY.md         |
| **Data minimization**                            | ✅     | Only collect what's needed        |
| **Parental access to data**                      | ☐      | Document data access process      |
| **Parental deletion rights**                     | ☐      | Document deletion process         |

### Data Boundary for Children

- [x] No names collected from students
- [x] No photos or videos
- [x] No location data
- [x] No contact information from students
- [x] Reports sent only to parent email

## Email Deliverability Best Practices

| Practice                      | Status | Notes                              |
| ----------------------------- | ------ | ---------------------------------- |
| **SPF record configured**     | ☐      | Add to DNS                         |
| **DKIM signing enabled**      | ☐      | Configure with SendGrid            |
| **DMARC policy set**          | ☐      | Start with p=none, monitor         |
| **Dedicated sending domain**  | ☐      | e.g., mail.stepwise.com            |
| **Consistent "From" address** | ☐      | Use noreply@stepwise.com           |
| **List hygiene**              | ✅     | Remove bounces, honor unsubscribes |
| **Throttling implemented**    | ✅     | 5 session reports/24h, 1 digest/7d |
| **Idempotency checks**        | ✅     | Prevent duplicate sends            |

### Email Authentication DNS Records

```
# SPF (add to DNS TXT record for domain)
v=spf1 include:sendgrid.net ~all

# DKIM (configured in SendGrid, add CNAME records)
# See SendGrid dashboard for specific records

# DMARC (add to DNS TXT record for _dmarc.domain)
v=DMARC1; p=none; rua=mailto:dmarc-reports@example.com
```

## Pre-Launch Checklist

### Legal Documents

- [ ] Privacy Policy reviewed by attorney
- [ ] Terms of Service reviewed by attorney
- [ ] Cookie notice (if applicable)
- [ ] Physical address added to email footer

### Technical Implementation

- [x] Unsubscribe endpoint working
- [x] Send-time suppression enforced
- [x] Email throttling active
- [x] Idempotency prevents duplicates
- [ ] SPF/DKIM/DMARC configured
- [ ] Bounce handling configured in SendGrid

### Testing

- [x] Unsubscribe flow tested (all types)
- [x] Email footer contains unsubscribe link
- [x] Preference changes take immediate effect
- [ ] Test emails pass spam filters
- [ ] Mobile email rendering tested

## Ongoing Compliance

### Monthly

- [ ] Review bounce rates
- [ ] Check spam complaint rates (<0.1%)
- [ ] Verify unsubscribe processing

### Quarterly

- [ ] Review and update privacy policy if needed
- [ ] Audit data retention
- [ ] Test unsubscribe flow

### Annually

- [ ] Full compliance review
- [ ] Legal document updates
- [ ] Security audit

## Contact Points

| Role              | Contact                     |
| ----------------- | --------------------------- |
| Privacy questions | [PRIVACY_EMAIL_PLACEHOLDER] |
| Abuse reports     | [ABUSE_EMAIL_PLACEHOLDER]   |
| General support   | [SUPPORT_EMAIL_PLACEHOLDER] |

---

_Last reviewed: [DATE]_
