"""
Agent Gamma — Shareable Content Writer & Delivery Agent
========================================================
Responsibility:
  Takes Beta's per-paper summaries and Alpha's paper list (for PubMed links)
  and produces SHAREABLE CONTENT for each paper — formatted for WhatsApp and
  email, with key points and a 'Read More' link to the original PubMed source.

  Optionally delivers content via WhatsApp (Twilio) and email (SendGrid).

Input:
  • topic         — research topic
  • paper_list    — Alpha's output (contains PubMed links per paper)
  • summaries     — Beta's output (per-paper clinical summaries)

Output per paper:
  • WhatsApp message: emoji-formatted, 150–200 words, key bullet points + Read More link
  • HTML email body: clean HTML version of the same content
  • Delivery status from WhatsApp/email APIs
"""

import re
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config import get_llm
from tools import send_email, send_whatsapp

# ── Prompt: Write shareable content per paper ─────────────────────────────────

_CONTENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """\
You are Agent Gamma, a medical communications specialist for Mankind Pharma (India).

You receive:
  1. A list of research papers with their PubMed links (from Agent Alpha)
  2. Clinical summaries for each paper (from Agent Beta)

Your job is to produce a SHAREABLE MESSAGE for EACH paper — formatted for
WhatsApp and email, ready to be sent by Jijo (BU Head / PMT) to doctors.

For EVERY paper, write the following:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### MESSAGE <N>: <PAPER TITLE (shortened to max 10 words)>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**WHATSAPP VERSION** (plain text, 150–200 words):
Use this EXACT format for the WhatsApp message:

────────────────────────────────────
📋 *[Short title — max 12 words]*

Hi Doctor,

[1–2 sentence hook: what's the key finding and why it matters]

*Key Highlights:*
• [Specific point 1 with number/stat]
• [Specific point 2 with number/stat]
• [Specific point 3 with number/stat]

[1 sentence on clinical relevance for Indian patients]

📖 *Read full paper:* [EXACT PubMed URL from Alpha's paper list]

— Pinnacle Research Team | Mankind Pharma
────────────────────────────────────

**HTML EMAIL VERSION**:
<h3>[Full paper title]</h3>
<p>[1–2 sentence introduction]</p>
<p><strong>Key Highlights:</strong></p>
<ul>
  <li>[Point 1 with stat]</li>
  <li>[Point 2 with stat]</li>
  <li>[Point 3 with stat]</li>
</ul>
<p>[Clinical relevance for India]</p>
<p>📖 <a href="[EXACT PubMed URL]">Read full paper on PubMed</a></p>
<p><em>— Pinnacle Research Team | Mankind Pharma</em></p>

---

After ALL papers, add:

═══════════════════════════════════════════════════════════════
AGENT GAMMA — CONTENT READY
Messages Prepared: <N>
Delivery Channel: WhatsApp + Email
═══════════════════════════════════════════════════════════════

CRITICAL RULES:
- The PubMed URL in each message MUST be the EXACT URL from Agent Alpha's paper list
  (format: https://pubmed.ncbi.nlm.nih.gov/<PMID>/)
  Do NOT fabricate or guess any PubMed links — copy them exactly as given
- Keep WhatsApp messages concise: 150–200 words max
- Use real statistics from Beta's summaries
- Write for a busy specialist doctor — direct and clinically relevant
- Tone: collegial, not promotional — "evidence says" not "our drug does"
"""),
    ("human", """\
Topic: {topic}

=== Agent Alpha's Paper List (contains PubMed links) ===
{paper_list}

=== Agent Beta's Clinical Summaries ===
{summaries}
"""),
])

# ── HTML email wrapper ────────────────────────────────────────────────────────

_EMAIL_WRAP_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """\
You are formatting a batch of research paper summaries as a single HTML email digest.
Wrap all the individual HTML sections into a clean, mobile-friendly email body.
Add a header with the topic name and a footer with "Pinnacle Research Team | Mankind Pharma".
Return ONLY the HTML body content — no <html>/<body> wrapper tags needed.
Keep it professional and easy to read on mobile.
"""),
    ("human", "Topic: {topic}\n\nContent:\n{content}"),
])


# ── Main runner ───────────────────────────────────────────────────────────────

def run_gamma(topic: str, paper_list: str, summaries: str) -> dict:
    """
    Run Agent Gamma: write shareable content per paper and deliver via
    WhatsApp and email.

    Args:
        topic:      The research topic.
        paper_list: Agent Alpha's structured paper list (includes PubMed URLs).
        summaries:  Agent Beta's per-paper clinical summaries.

    Returns:
        dict with:
          'content'         — formatted shareable messages (WhatsApp + HTML) per paper
          'whatsapp_status' — delivery result from Twilio
          'email_status'    — delivery result from SendGrid
    """
    llm = get_llm(temperature=0.25)

    # Step 1: Generate shareable content per paper
    content_chain = _CONTENT_PROMPT | llm | StrOutputParser()
    content = content_chain.invoke({
        "topic":      topic,
        "paper_list": paper_list,
        "summaries":  summaries,
    })

    # Step 2: Build HTML email digest
    html_chain = _EMAIL_WRAP_PROMPT | llm | StrOutputParser()
    html_body  = html_chain.invoke({"topic": topic, "content": content})

    # Step 3: Extract first WhatsApp message for delivery (avoid sending all at once)
    wa_message = _extract_first_whatsapp_message(content, topic)

    # Step 4: Deliver
    subject          = f"Research Update: {topic}"
    whatsapp_status  = send_whatsapp(wa_message)
    email_status     = send_email(subject=subject, body_html=html_body)

    return {
        "content":          content,
        "html_body":        html_body,
        "whatsapp_status":  whatsapp_status,
        "email_status":     email_status,
    }


def _extract_first_whatsapp_message(content: str, topic: str) -> str:
    """
    Extract the first WhatsApp-formatted message from Gamma's output.
    Falls back to a compact summary if parsing fails.
    """
    # Try to find the WhatsApp section between the dashes
    match = re.search(
        r"────+\n(.+?)────+",
        content,
        re.DOTALL,
    )
    if match:
        return match.group(1).strip()

    # Fallback: use first 1000 chars of content
    return f"*Research Update: {topic}*\n\n{content[:1000]}..."
