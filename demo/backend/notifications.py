"""
Notification Service — in-app + email stubs.
In-app notifications stored in DB. Email via SendGrid (configured in .env).
"""
import os
from datetime import datetime


def notify_ma_new_content(store, content_id: str, title: str, specialty: str, division: str):
    """Notify MA team when a new content card is ready for review."""
    store.add_notification(
        type="new_content",
        content_id=content_id,
        title=f"New content ready for review: {title}",
        message=f"Agent pipeline generated a new {specialty} article for {division} division. Please review.",
        division=division,
    )
    _send_email_stub("MA Review Required", f"New content ready: {title}", recipient_role="ma_team")


def notify_ma_improvement_ready(store, content_id: str, title: str, version: int, division: str):
    """Notify MA team when an improved version is ready for re-review."""
    store.add_notification(
        type="improvement_ready",
        content_id=content_id,
        title=f"Revised content ready (v{version}): {title}",
        message=f"The AI pipeline has incorporated your feedback. Version {version} is ready for re-review.",
        division=division,
    )
    _send_email_stub("Revised Content Ready", f"v{version} ready: {title}", recipient_role="ma_team")


def notify_bu_content_approved(store, content_id: str, title: str, division: str):
    """Notify BU Head when content is approved and ready to share."""
    store.add_notification(
        type="content_approved",
        content_id=content_id,
        title=f"Content approved — ready to share: {title}",
        message=f"Medical Affairs has approved this content. You can now share it with your doctors.",
        division=division,
    )
    _send_email_stub("Content Approved", f"Ready to share: {title}", recipient_role="bu_head")


def _send_email_stub(subject: str, body: str, recipient_role: str):
    """Email stub — logs to console. Wire up SendGrid when SENDGRID_API_KEY is set."""
    api_key = os.getenv("SENDGRID_API_KEY")
    if not api_key or api_key.startswith("your_"):
        print(f"[Notification] EMAIL STUB -> [{recipient_role}] {subject}: {body}")
        return
    # Production: send via SendGrid
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        recipients = {
            "ma_team": os.getenv("MA_TEAM_EMAIL", ""),
            "bu_head": os.getenv("BU_HEAD_EMAIL", ""),
        }
        to = recipients.get(recipient_role, "")
        if not to:
            return
        msg = Mail(
            from_email=os.getenv("EMAIL_FROM", "pinnacle@mankind.com"),
            to_emails=to,
            subject=f"[PinnacleIQ] {subject}",
            plain_text_content=body,
        )
        SendGridAPIClient(api_key).send(msg)
        print(f"[Notification] Email sent -> {to}: {subject}")
    except Exception as e:
        print(f"[Notification] Email failed: {e}")
