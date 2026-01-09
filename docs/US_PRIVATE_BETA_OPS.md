# US Private Beta Operations Guide

## Overview

This document outlines operational procedures for StepWise's US private beta program, including recruitment, feedback collection, and compliance requirements.

**Target Audience**: US families with students in Grades 4–9

**Beta Goal**: Validate product-market fit and gather early user feedback before public launch.

**Related**: [US Beta Recruitment Kit](./US_BETA_RECRUITMENT_KIT.md) — Ready-to-use templates for Reddit, Discord, email, and PMF surveys.

---

## Beta Access Control

### Access Code System

StepWise uses a simple access code system to control beta access:

1. **Environment Variable**: Set `BETA_ACCESS_CODE` in backend environment
2. **Header Check**: Protected endpoints require `X-Beta-Code` header
3. **Frontend Gate**: Modal prompts for code on first visit
4. **Storage**: Code saved in browser localStorage

**Protected Endpoints**:

- `POST /api/v1/sessions/start`
- `POST /api/v1/sessions/{id}/respond`
- `POST /api/v1/sessions/{id}/reveal`
- `POST /api/v1/sessions/{id}/complete`

**Non-Protected** (always accessible):

- Health checks, docs
- Unsubscribe endpoints
- Feedback endpoints
- Terms/Privacy pages

### Generating Access Codes

For the beta period, use a single shared code distributed to all beta testers. Example:

```bash
# In backend .env
BETA_ACCESS_CODE=stepwise-beta-2026
```

---

## Recruitment

### Target Profile

- **Geography**: United States only
- **Role**: Parents/guardians of students
- **Student Grade**: 4th through 9th grade
- **Interest**: Supplemental math education, homework help

### Recruitment Channels

#### Reddit

**Target Subreddits**:

- r/Parenting
- r/homeschool
- r/Teachers (for referrals to parents)
- r/learnmath
- r/education

**Sample Post Template**:

```
Title: [US Beta Testers Wanted] Free Socratic Math Tutoring App for Grades 4-9

Hi r/Parenting!

I'm looking for US families to test StepWise, a free math tutoring app
that helps kids learn to solve problems themselves (instead of just
giving answers).

How it works:
- Student enters a math problem
- App provides layered hints: Concept → Strategy → Step-by-step
- Parent receives email summaries of learning sessions

Looking for:
- Parents of kids in grades 4-9
- Located in the US
- 10-15 minutes/week commitment

What you get:
- Free access during beta
- Direct line to product team for feedback
- Help shape the final product

DM me if interested and I'll send a beta access code!
```

#### Discord

**Target Servers**:

- Homeschool communities
- Parent support groups
- Education-focused servers

**Approach**: Request permission from mods before posting. Offer to do a brief Q&A.

#### Email Invite

For direct outreach to parents who've expressed interest:

```
Subject: Your StepWise Beta Access Code

Hi [Name],

Thank you for your interest in the StepWise private beta!

Here's your access code: [BETA_CODE]

To get started:
1. Visit stepwise.app
2. Enter your beta code when prompted
3. Start with any math problem your child is working on

During the beta, we'd love your feedback:
- What's working well?
- What's confusing or frustrating?
- Would you pay for this if it saved you time?

Reply to this email anytime with thoughts, questions, or issues.

Thank you for helping us build something useful!

Best,
[Your Name]
StepWise Team
```

---

## PMF (Product-Market Fit) Measurement

### The Sean Ellis Test

**Core Question**: "How would you feel if you could no longer use StepWise?"

**Response Options**:

1. Very disappointed
2. Somewhat disappointed
3. Not disappointed

**PMF Threshold**: **40%+ selecting "Very disappointed"** indicates strong product-market fit.

### When to Survey

- After 3+ completed sessions per family
- At 2-week mark of active usage
- Before any major pivot decision

### Survey Implementation

The feedback modal in StepWise includes the PMF question. Track responses in `/api/v1/feedback`.

### Interpreting Results

| % Very Disappointed | Interpretation | Action                          |
| ------------------- | -------------- | ------------------------------- |
| < 25%               | Weak fit       | Major pivot needed              |
| 25-40%              | Moderate fit   | Iterate on core value prop      |
| 40%+                | Strong fit     | Double down, prepare for launch |

---

## Email Communications

### Types of Emails

1. **Session Reports** (per-session, optional)
   - Sent immediately after session completion
   - Contains: performance summary, time spent, layer progression

2. **Weekly Digests** (weekly, optional)
   - Sent every Sunday
   - Contains: week's activity, progress trends, recommendations

### Compliance Requirements

#### CAN-SPAM Compliance

- **Unsubscribe**: Every email must include one-click unsubscribe link
- **Physical Address**: Include company address in footer
- **Honest Subject**: No misleading subject lines
- **Honor Opt-outs**: Process within 10 business days (we do immediately)

#### COPPA Compliance (Critical)

Since StepWise serves children under 13:

1. **Parental Consent**: Only parents/guardians provide email addresses
2. **No Direct Child Collection**: Never collect email/PII directly from children
3. **Minimal Data**: Only collect what's necessary for service
4. **Parent Control**: Parents can delete data at any time

**Implementation Notes**:

- Email field is labeled "Parent/Guardian Email"
- Email is optional, not required
- No accounts = minimal data footprint
- Student responses are not logged verbatim (privacy protection)

### Opt-Out Handling

Users can opt out via:

1. **Email Link**: One-click unsubscribe in every email
2. **API Endpoint**: `POST /api/v1/email/unsubscribe`
3. **Support Email**: Manual request to support@stepwise.app

**Endpoint**: `/api/v1/email/unsubscribe`

```json
{
  "email": "parent@example.com",
  "reason": "optional feedback"
}
```

---

## Beta Metrics to Track

### Engagement Metrics

- Sessions started per user per week
- Session completion rate (vs. revealed/abandoned)
- Layer progression: How many reach STEP? COMPLETED?
- Return rate: % of users who come back after first session

### Quality Metrics

- Confusion count per session (lower is better)
- Time per layer (indicates understanding speed)
- Reveal usage rate (lower is better for learning)

### PMF Metrics

- "Very disappointed" percentage (target: 40%+)
- Qualitative feedback themes
- Feature requests frequency

---

## Support & Escalation

### Common Issues

| Issue                       | Resolution                             |
| --------------------------- | -------------------------------------- |
| Beta code not working       | Verify code matches exactly, no spaces |
| Email not received          | Check spam, verify email address       |
| App won't load              | Clear localStorage, try incognito      |
| Math problem not recognized | Ensure problem has numbers/variables   |

### Escalation Path

1. **Self-Service**: FAQ/docs
2. **Email Support**: support@stepwise.app
3. **Direct Slack**: For beta testers, direct channel to product team

---

## Timeline & Milestones

| Week | Goal                | Success Criteria                         |
| ---- | ------------------- | ---------------------------------------- |
| 1-2  | Recruit 20 families | 20 active beta codes distributed         |
| 3-4  | Initial feedback    | 50+ sessions completed, first PMF survey |
| 5-6  | Iterate             | Address top 3 pain points                |
| 7-8  | Scale test          | 50 families, 200+ sessions               |
| 9-10 | PMF assessment      | 40%+ "very disappointed"                 |

---

## Quick Reference

**Beta Code Env Var**: `BETA_ACCESS_CODE`
**Protected Header**: `X-Beta-Code`
**LocalStorage Key**: `beta_access_code`
**PMF Threshold**: 40% "very disappointed"
**Support Email**: support@stepwise.app
**Unsubscribe Endpoint**: `POST /api/v1/email/unsubscribe`
