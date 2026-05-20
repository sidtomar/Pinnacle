"""Email delivery via SendGrid."""
import os

import sendgrid
from sendgrid.helpers.mail import Mail, To


def send_email(subject: str, body_html: str, recipients: list[str] | None = None) -> dict:
    """
    Send an HTML email via SendGrid.

    recipients: list of email addresses.
                Falls back to EMAIL_RECIPIENTS env var if not provided.
    Returns: dict with HTTP status code and response body.
    """
    if recipients is None:
        raw = os.getenv("EMAIL_RECIPIENTS", "")
        recipients = [r.strip() for r in raw.split(",") if r.strip()]

    if not recipients:
        return {"error": "No email recipients configured."}

    sg = sendgrid.SendGridAPIClient(api_key=os.environ["SENDGRID_API_KEY"])

    message = Mail(
        from_email=(os.environ["EMAIL_FROM"], os.getenv("EMAIL_FROM_NAME", "Research Bot")),
        to_emails=[To(r) for r in recipients],
        subject=subject,
        html_content=body_html,
    )

    try:
        response = sg.send(message)
        return {"status_code": response.status_code, "body": response.body}
    except Exception as exc:
        return {"error": str(exc)}
