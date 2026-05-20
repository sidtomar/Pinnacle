"""
Agent Gamma — Article Writer & Delivery Agent

Takes Beta's insights and:
1. Writes a concise, doctor-friendly article (suitable for WhatsApp/email)
2. Delivers it via WhatsApp (Twilio) and Email (SendGrid)
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config import get_llm
from tools import send_email, send_whatsapp

_ARTICLE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
You are Agent Gamma, a medical communications specialist.
You write short, clear, impactful articles for doctors — busy professionals who need
the most important information fast.

Guidelines:
- Maximum 400 words
- Use plain language (avoid jargon unless clinically necessary)
- Structure: Hook → Key Finding → Why it Matters → What To Do
- End with a one-line action item
- Tone: professional, collegial, direct

The article will be sent via WhatsApp and email, so format it for plain text
(no markdown bold/italics, use capitals for emphasis if needed).
"""),
    ("human", "Insights Report:\n\n{insights}\n\nTopic: {topic}"),
])

_EMAIL_BODY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
Convert the plain-text article into a clean HTML email body.
Use simple HTML: <h2> for headings, <p> for paragraphs, <ul>/<li> for lists.
Add a professional sign-off: "Pinnacle Research Team".
Keep it mobile-friendly and clean.
Return ONLY the HTML body content (no <html>/<body> wrapper tags).
"""),
    ("human", "{article}"),
])


def run_gamma(topic: str, insights: str) -> dict:
    """
    Run Agent Gamma: write the article and deliver via WhatsApp + email.
    Returns a dict with the article text and delivery status.
    """
    llm = get_llm(temperature=0.3)

    # Step 1: Write the article
    article_chain = _ARTICLE_PROMPT | llm | StrOutputParser()
    article = article_chain.invoke({"insights": insights, "topic": topic})

    # Step 2: Convert to HTML for email
    html_chain = _EMAIL_BODY_PROMPT | llm | StrOutputParser()
    html_body = html_chain.invoke({"article": article})

    # Step 3: Deliver
    subject = f"Research Update: {topic}"
    whatsapp_status = send_whatsapp(f"*{subject}*\n\n{article}")
    email_status = send_email(subject=subject, body_html=html_body)

    return {
        "article": article,
        "html_body": html_body,
        "whatsapp_status": whatsapp_status,
        "email_status": email_status,
    }
