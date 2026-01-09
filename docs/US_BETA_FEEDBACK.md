# StepWise Beta Feedback Form Specification

This document defines the feedback form for the StepWise private beta, including the in-app modal and a copy-paste Google Form template.

## Purpose

Collect structured feedback from beta users to measure product-market fit and identify areas for improvement.

## In-App Feedback Modal

The feedback modal is accessible via the "Feedback" button in the app (data-testid="nav-feedback").

### Questions

#### 1. PMF Question (Sean Ellis)

**Question**: How would you feel if you could no longer use StepWise?

| Option                | Value                   |
| --------------------- | ----------------------- |
| Very disappointed     | `very_disappointed`     |
| Somewhat disappointed | `somewhat_disappointed` |
| Not disappointed      | `not_disappointed`      |

> **PMF Benchmark**: 40%+ selecting "Very disappointed" indicates product-market fit.

#### 2. What Worked Best?

**Question**: What did you find most valuable about StepWise?

- Free text (max 500 characters)
- Optional

#### 3. What Was Confusing?

**Question**: What was confusing or frustrating?

- Free text (max 500 characters)
- Optional

#### 4. Would You Pay?

**Question**: Would you pay for StepWise?

| Option          | Value            |
| --------------- | ---------------- |
| Yes, definitely | `yes_definitely` |
| Yes, probably   | `yes_probably`   |
| Not sure        | `not_sure`       |
| Probably not    | `probably_not`   |
| Definitely not  | `definitely_not` |

#### 5. Child's Grade Level

**Question**: What grade is your child in?

| Option  | Value     |
| ------- | --------- |
| Grade 4 | `grade_4` |
| Grade 5 | `grade_5` |
| Grade 6 | `grade_6` |
| Grade 7 | `grade_7` |
| Grade 8 | `grade_8` |
| Grade 9 | `grade_9` |

#### 6. Parent Email (Optional)

**Question**: Your email (optional, for follow-up questions)

- Email field with validation
- Optional

#### 7. Consent Checkbox

**Label**: I agree that StepWise may contact me about my feedback. My email will only be used for product research and will not be shared or used for marketing.

- Required if email is provided

---

## Google Form Template

Copy-paste the following structure to create a Google Form:

### Form Title

**StepWise Beta Feedback**

### Form Description

```
Thank you for participating in the StepWise private beta! Your feedback helps us improve the learning experience for families like yours.

This survey takes about 2 minutes to complete.
```

### Questions

---

**Question 1** (Required, Multiple Choice)

```
How would you feel if you could no longer use StepWise?

○ Very disappointed
○ Somewhat disappointed
○ Not disappointed
```

---

**Question 2** (Optional, Long Answer)

```
What did you find most valuable about StepWise?

[Long answer text box]
```

---

**Question 3** (Optional, Long Answer)

```
What was confusing or frustrating?

[Long answer text box]
```

---

**Question 4** (Required, Multiple Choice)

```
Would you pay for StepWise?

○ Yes, definitely
○ Yes, probably
○ Not sure
○ Probably not
○ Definitely not
```

---

**Question 5** (Required, Dropdown)

```
What grade is your child in?

▼ Select grade
  Grade 4
  Grade 5
  Grade 6
  Grade 7
  Grade 8
  Grade 9
```

---

**Question 6** (Optional, Short Answer)

```
Your email (optional, for follow-up questions)

[Short answer text box - email validation]
```

---

**Question 7** (Required if Q6 answered, Checkbox)

```
□ I agree that StepWise may contact me about my feedback. My email will only be used for product research and will not be shared or used for marketing.
```

---

### Confirmation Message

```
Thank you for your feedback! Your input helps us build a better learning experience for families.
```

---

## Data Storage (In-App)

Feedback submitted via the in-app modal is stored in the backend database:

| Field         | Type     | Description                       |
| ------------- | -------- | --------------------------------- |
| id            | UUID     | Primary key                       |
| created_at    | DateTime | Submission timestamp              |
| locale        | String   | User's locale (e.g., "en-US")     |
| grade_level   | String   | Child's grade (grade_4 - grade_9) |
| pmf_answer    | String   | PMF question response             |
| would_pay     | String   | Payment intent response           |
| what_worked   | Text     | Free text - what worked           |
| what_confused | Text     | Free text - what was confusing    |
| email         | String   | Optional parent email             |

### Privacy Notes

- **No child data**: We do not store child names or identifiers
- **No raw student responses**: Feedback is about the product, not student work
- **Email is optional**: Only stored if explicitly provided with consent
- **Research use only**: Email used only for product research follow-up

---

## Analysis

### PMF Score Calculation

```
PMF Score = (Count of "Very disappointed") / (Total responses) × 100

Target: ≥ 40%
```

### Key Metrics to Track

1. **PMF Score**: % very disappointed
2. **Payment Intent**: % yes_definitely + yes_probably
3. **Grade Distribution**: Which grades are most engaged
4. **Common Pain Points**: Themes in "what was confusing"
5. **Value Props**: Themes in "what worked best"
