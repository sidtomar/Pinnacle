"""Twilio WhatsApp delivery tool."""
import os

from twilio.rest import Client


def send_whatsapp(message: str, recipients: list[str] | None = None) -> dict:
    """
    Send a WhatsApp message to one or more recipients via Twilio.

    recipients: list of 'whatsapp:+<number>' strings.
                Falls back to WHATSAPP_RECIPIENTS env var if not provided.
    Returns: dict with status per recipient.
    """
    client = Client(
        os.environ["TWILIO_ACCOUNT_SID"],
        os.environ["TWILIO_AUTH_TOKEN"],
    )
    from_number = os.environ["TWILIO_WHATSAPP_FROM"]

    if recipients is None:
        raw = os.getenv("WHATSAPP_RECIPIENTS", "")
        recipients = [r.strip() for r in raw.split(",") if r.strip()]

    if not recipients:
        return {"error": "No WhatsApp recipients configured."}

    results = {}
    for to in recipients:
        try:
            msg = client.messages.create(body=message, from_=from_number, to=to)
            results[to] = {"sid": msg.sid, "status": msg.status}
        except Exception as exc:
            results[to] = {"error": str(exc)}

    return results
