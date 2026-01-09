# US Private Beta Recruitment Kit

> **Ready-to-use templates for recruiting US beta testers.** Copy, customize placeholders, and deploy.

---

## Placeholders Reference

Before using any template, replace these placeholders with your actual values:

| Placeholder                     | Description                                           |
| ------------------------------- | ----------------------------------------------------- |
| `<APP_URL>`                     | Your app URL (e.g., `https://stepwise.app`)           |
| `<BETA_CODE>`                   | The beta access code to distribute                    |
| `<PMF_FORM_URL>`                | Link to your PMF survey (Google Form, Typeform, etc.) |
| `<PRIVACY_URL>`                 | Link to your Privacy Policy page                      |
| `<TERMS_URL>`                   | Link to your Terms of Service page                    |
| `<UNSUBSCRIBE_PREFERENCES_URL>` | One-click unsubscribe/preferences page URL            |
| `<COMPANY_POSTAL_ADDRESS>`      | Physical mailing address (required for CAN-SPAM)      |
| `<SUPPORT_EMAIL>`               | Support contact email                                 |

---

## Generating Beta Codes

Use the included script to generate unique beta access codes:

```bash
# Generate 100 codes (default) to CSV file
python3 scripts/generate_beta_codes.py

# Generate custom number of codes
python3 scripts/generate_beta_codes.py -n 50

# Output to specific file
python3 scripts/generate_beta_codes.py -o my_codes.csv

# Print codes to stdout (for piping)
python3 scripts/generate_beta_codes.py -n 10 --stdout
```

### CSV Output Format

The generated CSV includes tracking columns:

| Column          | Description                         |
| --------------- | ----------------------------------- |
| `code`          | UUIDv4 beta code                    |
| `assigned_to`   | Email/name of recipient (fill in)   |
| `assigned_date` | Date code was distributed (fill in) |
| `used`          | Whether code was redeemed (fill in) |

### Setting the Backend Environment

After generating codes, set one as the `BETA_ACCESS_CODE` environment variable:

```bash
# Local development
export BETA_ACCESS_CODE="your-generated-uuid-here"

# Fly.io staging
fly secrets set BETA_ACCESS_CODE="your-generated-uuid-here" -a stepwise-backend-staging
```

### Single vs Multiple Codes

**Option A: Single shared code** (simpler)

- Generate one code, use it in all templates
- Set as `BETA_ACCESS_CODE` env var
- Pros: Simple to manage
- Cons: Can't revoke individual access, no tracking

**Option B: Per-user codes** (more control)

- Generate many codes, assign one per tester
- Requires backend changes to validate against a list
- Pros: Can revoke, track usage, limit per code
- Cons: More complex

For initial beta, **Option A is recommended**. Switch to Option B if you need to revoke access or track individual testers.

---

## Reddit Templates

### Version A: Parent-Focused (Recommended for r/Parenting, r/homeschool)

```
Title: [US Beta Testers Wanted] Free Socratic Math Tutoring App for Grades 4-9

Hi! I'm looking for US families to test StepWise, a free math tutoring app that helps kids learn to solve problems themselves (instead of just giving away answers).

**How it works:**
- Student enters a math problem they're stuck on
- App provides layered hints: Concept → Strategy → Step-by-step
- Parent receives optional email summaries of learning sessions

**What we're looking for:**
- Parents of kids in grades 4-9
- Located in the US
- 10-15 minutes/week to try it out

**What you get:**
- Free access during beta
- Direct line to the product team
- Help shape what we build next

**Interested?** DM me and I'll send you a beta access code!

Or go directly to <APP_URL> and use code: <BETA_CODE>

Questions? Happy to answer in the comments.
```

### Version B: Education-Focused (Recommended for r/learnmath, r/education)

```
Title: [Beta] Math tutoring app that teaches problem-solving, not just answers (Grades 4-9, US)

We built StepWise because we were frustrated with apps that just give kids the answer. Ours uses a Socratic approach—layered hints that guide students to figure it out themselves.

**The approach:**
1. Student enters their math problem
2. First hint: conceptual guidance ("What type of problem is this?")
3. Second hint: strategy ("What's the first step?")
4. Third hint: step-by-step walkthrough (only if still stuck)

**Currently in private beta** for US families with students in grades 4-9.

Looking for feedback on:
- Does the hint progression make sense?
- Is the difficulty appropriate for the grade level?
- What's missing?

Try it: <APP_URL>
Beta code: <BETA_CODE>

Would love honest feedback—especially what doesn't work.
```

---

## Discord Blurb

For posting in homeschool servers, parent groups, or education communities:

```
Hey everyone! Looking for a few US families to try our free math tutoring app (grades 4-9).

It's called StepWise—instead of giving answers, it guides kids through solving problems with layered hints. Parents can optionally get email summaries.

We're in private beta and want real feedback before launch.

Link: <APP_URL>
Code: <BETA_CODE>

Takes about 10 min to try. Happy to answer questions here!
```

---

## Email Invite Template

For direct outreach to interested parents:

```
Subject: Your StepWise Beta Access Code

Hi [NAME],

Thank you for your interest in the StepWise private beta!

Here's your access code: <BETA_CODE>

**Getting started:**
1. Go to <APP_URL>
2. Enter your beta code when prompted
3. Try any math problem your child is working on

**During the beta, we'd love to hear:**
- What's working well?
- What's confusing or frustrating?
- Would you pay for this if it saved you time helping with homework?

Reply to this email anytime, or fill out our quick feedback form: <PMF_FORM_URL>

Thank you for helping us build something useful!

Best,
[YOUR NAME]
StepWise Team

---
Privacy Policy: <PRIVACY_URL>
Terms of Service: <TERMS_URL>
```

---

## PMF Survey Structure (Google Form)

Create a Google Form with these questions:

### Required Questions

**Q1: How would you feel if you could no longer use StepWise?**

- Very disappointed
- Somewhat disappointed
- Not disappointed

> _This is the Sean Ellis test. Target: 40%+ "Very disappointed" = product-market fit._

**Q2: What type of person do you think would benefit most from StepWise?**
_(Open text)_

**Q3: What is the main benefit you get from StepWise?**
_(Open text)_

### Optional Questions

**Q4: How can we improve StepWise for you?**
_(Open text)_

**Q5: What grade is your child in?**

- 4th grade
- 5th grade
- 6th grade
- 7th grade
- 8th grade
- 9th grade

**Q6: How often does your child need help with math homework?**

- Daily
- A few times a week
- Once a week
- Rarely

**Q7: May we follow up with you via email?**

- Yes
- No

**Q8: Email address (optional)**
_(Short answer)_

---

## Compliance Footer

Include this footer in **all marketing emails**:

```
---

You're receiving this because you signed up for the StepWise beta program.

Manage preferences or unsubscribe: <UNSUBSCRIBE_PREFERENCES_URL>
(One click—no login required. Unsubscribe requests are processed promptly, within 10 business days. This unsubscribe mechanism will remain available for at least 30 days.)

Questions? Contact us at <SUPPORT_EMAIL>

<COMPANY_POSTAL_ADDRESS>

Privacy Policy: <PRIVACY_URL> | Terms: <TERMS_URL>
```

---

## COPPA-Aware Note

Include this note wherever users provide contact information:

```
Important: Parent or guardian should provide the email address.
Children should not enter personal information directly.
StepWise collects minimal data and does not require accounts.
```

For the onboarding flow or email input fields, use this label:

```
Parent/Guardian Email (optional)
```

---

## Pre-Launch Checklist

Before recruiting beta testers, verify:

- [ ] Beta codes generated: `python3 scripts/generate_beta_codes.py`
- [ ] `<APP_URL>` is live and accessible
- [ ] `<BETA_CODE>` is set in backend environment (`BETA_ACCESS_CODE`)
- [ ] `<PRIVACY_URL>` page exists and is accurate
- [ ] `<TERMS_URL>` page exists and is accurate
- [ ] `<UNSUBSCRIBE_PREFERENCES_URL>` works (one-click, no login)
- [ ] `<PMF_FORM_URL>` survey is created and tested
- [ ] `<SUPPORT_EMAIL>` is monitored
- [ ] `<COMPANY_POSTAL_ADDRESS>` is valid and included in email footer
- [ ] Email templates render correctly (test send to yourself)
- [ ] Beta gate modal appears correctly in frontend
- [ ] Session reports and weekly digest emails work

---

## Quick Reference

| Asset                   | Template Location                                                               |
| ----------------------- | ------------------------------------------------------------------------------- |
| Reddit Post (Parent)    | [Version A](#version-a-parent-focused-recommended-for-rparenting-rhomeschool)   |
| Reddit Post (Education) | [Version B](#version-b-education-focused-recommended-for-rlearnmath-reducation) |
| Discord Blurb           | [Discord Blurb](#discord-blurb)                                                 |
| Email Invite            | [Email Invite Template](#email-invite-template)                                 |
| PMF Survey              | [PMF Survey Structure](#pmf-survey-structure-google-form)                       |
| Email Footer            | [Compliance Footer](#compliance-footer)                                         |
| COPPA Note              | [COPPA-Aware Note](#coppa-aware-note)                                           |
