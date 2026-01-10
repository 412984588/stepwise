#!/usr/bin/env python3
"""
monitor_unsubscribe_rate.py - SendGrid Unsubscribe Rate Monitor

Parses SendGrid Event Webhook JSON to calculate unsubscribe rates and alert
if the rate exceeds industry standards (2% threshold per Mailchimp/Litmus).

Usage:
    python scripts/monitor_unsubscribe_rate.py [--webhook-url URL] [--days N] [--threshold PERCENT]

Options:
    --webhook-url URL    SendGrid Event Webhook URL (default: from SENDGRID_WEBHOOK_URL env var)
    --days N             Number of days to analyze (default: 7)
    --threshold PERCENT  Alert threshold percentage (default: 2.0)
    --output FORMAT      Output format: text|json|github (default: text)

Environment Variables:
    SENDGRID_API_KEY        SendGrid API key for fetching events
    SENDGRID_WEBHOOK_URL    SendGrid Event Webhook URL (optional)

References:
    - Mailchimp: https://mailchimp.com/resources/email-marketing-benchmarks/
    - Litmus: https://www.litmus.com/blog/email-benchmarks/
    - SendGrid Event Webhook: https://docs.sendgrid.com/for-developers/tracking-events/event
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests


# Industry standard thresholds (per Mailchimp/Litmus)
UNSUBSCRIBE_RATE_WARNING = 2.0  # 2% - Warning threshold
UNSUBSCRIBE_RATE_CRITICAL = 5.0  # 5% - Critical threshold
SPAM_COMPLAINT_RATE_WARNING = 0.1  # 0.1% - Warning threshold


class SendGridEventMonitor:
    """Monitor SendGrid events and calculate unsubscribe rates."""

    def __init__(self, api_key: str):
        """
        Initialize SendGrid event monitor.

        Args:
            api_key: SendGrid API key
        """
        self.api_key = api_key
        self.base_url = "https://api.sendgrid.com/v3"

    def fetch_events(self, days: int = 7, event_types: Optional[List[str]] = None) -> List[Dict]:
        """
        Fetch events from SendGrid Event API.

        Args:
            days: Number of days to fetch events for
            event_types: List of event types to fetch (default: all)

        Returns:
            List of event dictionaries
        """
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Build query parameters
        params = {
            "start_time": int(start_date.timestamp()),
            "end_time": int(end_date.timestamp()),
            "limit": 1000,  # Max per request
        }

        if event_types:
            params["event"] = ",".join(event_types)  # type: ignore

        # Fetch events
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        all_events = []
        offset = 0

        while True:
            params["offset"] = offset

            response = requests.get(
                f"{self.base_url}/messages",
                headers=headers,
                params=params,
                timeout=30,
            )

            if response.status_code != 200:
                print(
                    f"Error fetching events: {response.status_code} {response.text}",
                    file=sys.stderr,
                )
                break

            data = response.json()
            events = data.get("messages", [])

            if not events:
                break

            all_events.extend(events)
            offset += len(events)

            # Check if we've fetched all events
            if len(events) < 1000:
                break

        return all_events

    def calculate_metrics(self, events: List[Dict]) -> Dict:
        """
        Calculate email metrics from events.

        Args:
            events: List of SendGrid event dictionaries

        Returns:
            Dictionary with calculated metrics
        """
        # Count events by type
        event_counts = {
            "delivered": 0,
            "unsubscribe": 0,
            "spamreport": 0,
            "bounce": 0,
            "dropped": 0,
            "deferred": 0,
        }

        for event in events:
            event_type = event.get("event", "").lower()
            if event_type in event_counts:
                event_counts[event_type] += 1

        # Calculate rates
        total_delivered = event_counts["delivered"]

        if total_delivered == 0:
            return {
                "total_delivered": 0,
                "unsubscribe_count": event_counts["unsubscribe"],
                "unsubscribe_rate": 0.0,
                "spam_complaint_count": event_counts["spamreport"],
                "spam_complaint_rate": 0.0,
                "bounce_count": event_counts["bounce"],
                "bounce_rate": 0.0,
                "status": "NO_DATA",
            }

        unsubscribe_rate = (event_counts["unsubscribe"] / total_delivered) * 100
        spam_complaint_rate = (event_counts["spamreport"] / total_delivered) * 100
        bounce_rate = (event_counts["bounce"] / total_delivered) * 100

        # Determine status
        status = "HEALTHY"
        if unsubscribe_rate >= UNSUBSCRIBE_RATE_CRITICAL:
            status = "CRITICAL"
        elif unsubscribe_rate >= UNSUBSCRIBE_RATE_WARNING:
            status = "WARNING"
        elif spam_complaint_rate >= SPAM_COMPLAINT_RATE_WARNING:
            status = "WARNING"

        return {
            "total_delivered": total_delivered,
            "unsubscribe_count": event_counts["unsubscribe"],
            "unsubscribe_rate": round(unsubscribe_rate, 2),
            "spam_complaint_count": event_counts["spamreport"],
            "spam_complaint_rate": round(spam_complaint_rate, 2),
            "bounce_count": event_counts["bounce"],
            "bounce_rate": round(bounce_rate, 2),
            "dropped_count": event_counts["dropped"],
            "deferred_count": event_counts["deferred"],
            "status": status,
        }


def format_text_output(metrics: Dict, days: int) -> str:
    """
    Format metrics as human-readable text.

    Args:
        metrics: Metrics dictionary
        days: Number of days analyzed

    Returns:
        Formatted text output
    """
    status_emoji = {
        "HEALTHY": "✅",
        "WARNING": "⚠️",
        "CRITICAL": "❌",
        "NO_DATA": "ℹ️",
    }

    emoji = status_emoji.get(metrics["status"], "❓")

    output = f"""
{emoji} SendGrid Email Metrics ({days} days)

Status: {metrics["status"]}

📊 Delivery Metrics:
  Total Delivered: {metrics["total_delivered"]:,}
  Bounced: {metrics["bounce_count"]:,} ({metrics["bounce_rate"]}%)
  Dropped: {metrics["dropped_count"]:,}
  Deferred: {metrics["deferred_count"]:,}

📧 Engagement Metrics:
  Unsubscribes: {metrics["unsubscribe_count"]:,} ({metrics["unsubscribe_rate"]}%)
  Spam Complaints: {metrics["spam_complaint_count"]:,} ({metrics["spam_complaint_rate"]}%)

🎯 Thresholds:
  Unsubscribe Rate Warning: {UNSUBSCRIBE_RATE_WARNING}%
  Unsubscribe Rate Critical: {UNSUBSCRIBE_RATE_CRITICAL}%
  Spam Complaint Warning: {SPAM_COMPLAINT_RATE_WARNING}%

"""

    # Add warnings/recommendations
    if metrics["status"] == "CRITICAL":
        output += """
⚠️  CRITICAL: Unsubscribe rate exceeds {UNSUBSCRIBE_RATE_CRITICAL}%!

Recommended Actions:
1. Review recent email content for issues
2. Check email frequency (too many emails?)
3. Verify email list quality (purchased lists?)
4. Review email subject lines (misleading?)
5. Ensure unsubscribe link is prominent
"""
    elif metrics["status"] == "WARNING":
        output += """
⚠️  WARNING: Metrics approaching threshold

Recommended Actions:
1. Monitor closely over next 7 days
2. Review email content and frequency
3. Consider A/B testing subject lines
4. Verify email list hygiene
"""
    elif metrics["status"] == "HEALTHY":
        output += """
✅ All metrics within healthy range

Keep up the good work! Continue monitoring weekly.
"""
    elif metrics["status"] == "NO_DATA":
        output += """
ℹ️  No delivery data found for this period

Possible reasons:
- No emails sent in the last {days} days
- SendGrid API key lacks permissions
- Events not yet available (check SendGrid dashboard)
"""

    return output


def format_json_output(metrics: Dict) -> str:
    """
    Format metrics as JSON.

    Args:
        metrics: Metrics dictionary

    Returns:
        JSON string
    """
    return json.dumps(metrics, indent=2)


def format_github_output(metrics: Dict, days: int) -> str:
    """
    Format metrics for GitHub Actions Step Summary.

    Args:
        metrics: Metrics dictionary
        days: Number of days analyzed

    Returns:
        Markdown formatted output for GitHub
    """
    status_emoji = {
        "HEALTHY": "✅",
        "WARNING": "⚠️",
        "CRITICAL": "❌",
        "NO_DATA": "ℹ️",
    }

    emoji = status_emoji.get(metrics["status"], "❓")

    output = f"""
## {emoji} SendGrid Email Metrics ({days} days)

**Status**: {metrics["status"]}

### 📊 Delivery Metrics

| Metric | Count | Rate |
|--------|-------|------|
| Total Delivered | {metrics["total_delivered"]:,} | - |
| Bounced | {metrics["bounce_count"]:,} | {metrics["bounce_rate"]}% |
| Dropped | {metrics["dropped_count"]:,} | - |
| Deferred | {metrics["deferred_count"]:,} | - |

### 📧 Engagement Metrics

| Metric | Count | Rate | Threshold |
|--------|-------|------|-----------|
| Unsubscribes | {metrics["unsubscribe_count"]:,} | {metrics["unsubscribe_rate"]}% | {UNSUBSCRIBE_RATE_WARNING}% (warning) |
| Spam Complaints | {metrics["spam_complaint_count"]:,} | {metrics["spam_complaint_rate"]}% | {SPAM_COMPLAINT_RATE_WARNING}% (warning) |

"""

    # Add status-specific recommendations
    if metrics["status"] == "CRITICAL":
        output += """
### ⚠️ CRITICAL: Action Required

Unsubscribe rate exceeds critical threshold ({UNSUBSCRIBE_RATE_CRITICAL}%)!

**Recommended Actions**:
1. Review recent email content for issues
2. Check email frequency (too many emails?)
3. Verify email list quality
4. Review email subject lines
5. Ensure unsubscribe link is prominent
"""
    elif metrics["status"] == "WARNING":
        output += """
### ⚠️ WARNING: Monitor Closely

Metrics approaching threshold. Monitor over next 7 days.

**Recommended Actions**:
1. Review email content and frequency
2. Consider A/B testing subject lines
3. Verify email list hygiene
"""
    elif metrics["status"] == "HEALTHY":
        output += """
### ✅ Healthy Metrics

All metrics within acceptable range. Continue monitoring weekly.
"""

    return output


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor SendGrid unsubscribe rates and email metrics"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to analyze (default: 7)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=UNSUBSCRIBE_RATE_WARNING,
        help=f"Alert threshold percentage (default: {UNSUBSCRIBE_RATE_WARNING})",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json", "github"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    # Get SendGrid API key from environment
    api_key = os.getenv("SENDGRID_API_KEY")
    if not api_key:
        print("Error: SENDGRID_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Initialize monitor
    monitor = SendGridEventMonitor(api_key)

    # Fetch events
    print(f"Fetching SendGrid events for last {args.days} days...", file=sys.stderr)
    events = monitor.fetch_events(days=args.days)
    print(f"Fetched {len(events)} events", file=sys.stderr)

    # Calculate metrics
    metrics = monitor.calculate_metrics(events)

    # Format output
    if args.output == "json":
        print(format_json_output(metrics))
    elif args.output == "github":
        print(format_github_output(metrics, args.days))
    else:
        print(format_text_output(metrics, args.days))

    # Exit with error code if critical
    if metrics["status"] == "CRITICAL":
        sys.exit(1)
    elif metrics["status"] == "WARNING":
        sys.exit(0)  # Warning doesn't fail the script
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
