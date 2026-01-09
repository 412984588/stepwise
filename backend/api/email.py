"""Email management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from backend.database.engine import get_db
from backend.services.email_preference_service import EmailPreferenceService

router = APIRouter(prefix="/email", tags=["email"])


@router.get("/unsubscribe/{token}", response_class=HTMLResponse)
def unsubscribe_from_emails(
    token: str, type: str = "weekly_digest", db: Session = Depends(get_db)
) -> str:
    """
    Unsubscribe from emails.

    This endpoint is called when a parent clicks the unsubscribe link in their email.
    No authentication is required - the token acts as authorization.

    Args:
        token: Unsubscribe token from the email
        type: Which emails to unsubscribe from (weekly_digest, session_reports, all)
        db: Database session

    Returns:
        HTML confirmation page
    """
    if not token or len(token) != 36:
        raise HTTPException(status_code=400, detail="Invalid unsubscribe token format")

    if type not in ["weekly_digest", "session_reports", "all"]:
        return _generate_error_html(f"Invalid unsubscribe type: {type}")

    if type == "session_reports":
        success = EmailPreferenceService.mark_session_reports_unsubscribed(db, token)
    elif type == "all":
        success = EmailPreferenceService.mark_all_unsubscribed(db, token)
    else:
        success = EmailPreferenceService.mark_unsubscribed(db, token)

    if not success:
        return _generate_error_html("Invalid or expired unsubscribe link")

    return _generate_success_html(email_type=type, token=token)


def _generate_success_html(email_type: str = "weekly_digest", token: str = "") -> str:
    """Generate HTML confirmation page for successful unsubscribe."""
    if email_type == "session_reports":
        main_message = "You've been unsubscribed from <strong>session completion emails</strong>."
        other_type = "weekly learning reports"
        other_link_type = "weekly_digest"
    elif email_type == "all":
        main_message = "You've been unsubscribed from <strong>all StepWise emails</strong>."
        other_type = None
        other_link_type = None
    else:
        main_message = "You've been unsubscribed from <strong>weekly learning reports</strong>."
        other_type = "session completion emails"
        other_link_type = "session_reports"

    other_options_html = ""
    if other_type and token:
        other_options_html = f"""
            <div class="note" style="margin-top: 1.5rem; background: #f7fafc; border-left: 4px solid #4299e1; padding: 1rem; text-align: left; border-radius: 4px;">
                <p style="margin: 0 0 0.5rem 0; font-size: 0.95rem; color: #2d3748;"><strong>Manage Other Email Preferences</strong></p>
                <p style="margin: 0; font-size: 0.9rem; color: #4a5568;">
                    You're still subscribed to {other_type}.
                    If you'd like to unsubscribe from those as well,
                    <a href="/api/v1/email/unsubscribe/{token}?type={other_link_type}" style="color: #3b82f6; text-decoration: underline;">
                        click here
                    </a>.
                </p>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #6b7280;">
                    Or
                    <a href="/api/v1/email/unsubscribe/{token}?type=all" style="color: #ef4444; text-decoration: underline;">
                        unsubscribe from all emails
                    </a>.
                </p>
            </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Unsubscribed - StepWise</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}
            .container {{
                background: white;
                padding: 3rem 2rem;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 500px;
                margin: 1rem;
            }}
            .icon {{
                font-size: 4rem;
                margin-bottom: 1rem;
            }}
            h1 {{
                color: #2d3748;
                font-size: 1.75rem;
                margin-bottom: 1rem;
                font-weight: 600;
            }}
            p {{
                color: #4a5568;
                font-size: 1.1rem;
                line-height: 1.6;
                margin-bottom: 1.5rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">✓</div>
            <h1>You have been unsubscribed</h1>
            <p>{main_message}</p>
            <p style="font-size: 0.95rem; color: #6b7280;">This change takes effect immediately.</p>
            {other_options_html}
            <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;">
                <p style="margin: 0; font-size: 0.8rem; color: #9ca3af;">
                    Questions or concerns? <a href="mailto:support@stepwise.example.com" style="color: #6b7280;">Contact us</a>
                    &nbsp;|&nbsp;
                    <a href="mailto:abuse@stepwise.example.com" style="color: #6b7280;">Report abuse</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """


def _generate_error_html(
    message: str = "This unsubscribe link is not valid or may have already been used.",
) -> str:
    """Generate HTML error page for invalid/expired token."""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Invalid Link - StepWise</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}
            .container {{
                background: white;
                padding: 3rem 2rem;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 500px;
                margin: 1rem;
            }}
            .icon {{
                font-size: 4rem;
                margin-bottom: 1rem;
                color: #f56565;
            }}
            h1 {{
                color: #2d3748;
                font-size: 1.75rem;
                margin-bottom: 1rem;
                font-weight: 600;
            }}
            p {{
                color: #4a5568;
                font-size: 1.1rem;
                line-height: 1.6;
                margin-bottom: 1.5rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">⚠</div>
            <h1>Invalid or Expired Link</h1>
            <p>{message}</p>
            <p>If you continue to receive unwanted emails, please contact support.</p>
            <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;">
                <p style="margin: 0; font-size: 0.8rem; color: #9ca3af;">
                    <a href="mailto:support@stepwise.example.com" style="color: #6b7280;">Contact support</a>
                    &nbsp;|&nbsp;
                    <a href="mailto:abuse@stepwise.example.com" style="color: #6b7280;">Report abuse</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
