# StepWise US Private Beta

Welcome to the StepWise private beta! This document explains what StepWise is, how to run it locally, and important information about data and privacy.

## Who It's For

StepWise is designed for **US parents of students in Grades 4–9** who want to support their child's math learning at home. The beta is currently limited to English-speaking families in the United States.

## What StepWise Does

StepWise is a Socratic-style math tutoring system that helps students learn by guiding them through problems rather than giving away answers. When your child enters a math problem, StepWise provides layered hints—starting with conceptual guidance, then strategic approaches, and finally step-by-step help if needed. Parents receive session reports via email after each learning session, plus a weekly digest summarizing their child's progress, including metrics like problems attempted, completion rates, and areas that need more practice.

## How to Run Locally

### Prerequisites

- Python 3.11+
- Node.js 18+

### Quick Start

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-org/StepWise.git
   cd StepWise
   ```

2. **Start the development servers**:

   ```bash
   ./scripts/dev_up.sh
   ```

   This starts:
   - Backend API on http://localhost:8000
   - Frontend app on http://localhost:3000

3. **Stop the servers**:
   ```bash
   ./scripts/dev_down.sh
   ```

### First Use

1. Open http://localhost:3000 in your browser
2. Select your child's grade level
3. Enter a math problem (e.g., "Solve 2x + 5 = 11")
4. Follow the hints and respond with your understanding
5. Optionally provide your email to receive a learning report

## Data & Privacy

### What We Collect

| Data                    | Purpose                                 | Storage               |
| ----------------------- | --------------------------------------- | --------------------- |
| Math problems entered   | Generate personalized hints             | Session duration only |
| Hint interactions       | Track learning progress                 | Stored for reports    |
| Parent email (optional) | Send session reports and weekly digests | Until unsubscribe     |

### What We Do NOT Collect

- Student names or personal identifiers
- Photos, videos, or location data
- Social media accounts
- Any information directly from children

### Privacy Commitment

- **Parent email is used only for reports**: Session completion reports and weekly learning digests
- **Children's data is minimized**: We only store what's needed to provide hints and generate progress reports
- **No advertising**: We do not serve ads or share data with advertisers
- **No data selling**: We never sell personal information

For complete details, see our [Privacy Policy](./PRIVACY_POLICY.md) and [Terms of Service](./TERMS_OF_SERVICE.md).

## Email Communications

### What Emails You'll Receive

1. **Session Reports**: After your child completes a learning session, you'll receive a summary with insights and a PDF report
2. **Weekly Digests**: A summary of your child's learning activity over the past 7 days

### Email Compliance

- **Opt-out honored immediately**: When you unsubscribe, the change takes effect right away
- **One-click unsubscribe**: Every email includes an unsubscribe link—no login required
- **Granular control**: Unsubscribe from session reports, weekly digests, or all emails
- **Manage preferences**: Each email includes a link to manage your email preferences

### How to Unsubscribe

Click the "Unsubscribe" or "Manage email preferences" link in any email footer. You can:

- Unsubscribe from session reports only
- Unsubscribe from weekly digests only
- Unsubscribe from all StepWise emails

## COPPA Compliance

StepWise is designed with children's privacy in mind:

- **Parent/guardian provides email**: Children do not provide personal information
- **Parent controls communications**: All reports go to the parent email
- **No direct contact with children**: We only communicate with parents/guardians
- **Data minimization**: We collect only what's necessary for the tutoring experience
- **No behavioral advertising**: We do not target children with ads

## Beta Feedback

We'd love to hear from you! Use the **Feedback** button in the app to share:

- What's working well
- What's confusing
- Feature requests
- Bug reports

Your feedback helps us improve StepWise for all families.

## Support

For questions or issues during the beta:

- **Email**: support@stepwise.example.com
- **GitHub Issues**: [Report a bug](https://github.com/your-org/StepWise/issues)

---

_Thank you for participating in the StepWise private beta!_
