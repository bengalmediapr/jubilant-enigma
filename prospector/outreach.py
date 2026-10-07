"""Write personalized outreach with Claude, based on each lead's real audit."""

import json
import os

import anthropic
from pydantic import BaseModel

MODEL = "claude-opus-5-5"

SYSTEM = """You write cold outreach for Bengal Media PR (bengalmediapr.com), a web design \
and digital marketing studio in Puerto Rico. You write like a local person from Puerto Rico \
writing to a neighbor's business: warm, direct, short, no corporate fluff, no hype words, \
no fake urgency. Default to natural Puerto Rican Spanish (use "usted" unless the business \
is clearly casual); write in English only when asked.

Rules:
- Mention the business by name and refer to 1-3 specific problems from the audit. \
Never invent problems, numbers, or facts that are not in the audit data.
- Explain each problem as lost customers or lost sales, not as tech jargon.
- If the business has no website, or only a Facebook/Instagram page, the pitch is: \
customers searching Google can't find them, and social pages don't rank or take bookings.
- Offer one small, free, low-commitment next step (e.g. a free mockup of their new homepage, \
or a 10-minute call). One call to action only.
- Email body: under 120 words. No links other than bengalmediapr.com. No signature block \
(it is added later). No emojis in email.
- WhatsApp/DM message: under 60 words, friendly, for businesses reached by phone or Instagram."""


class Outreach(BaseModel):
    language: str
    subject: str
    email_body: str
    whatsapp_message: str
    top_issues: list[str]


def write_outreach(client: anthropic.Anthropic, lead: dict, audit: dict | None, language: str = "es") -> Outreach:
    facts = {
        "business": lead.get("name"),
        "category": lead.get("type") or lead.get("category"),
        "municipio": lead.get("municipio"),
        "google_rating": lead.get("rating"),
        "google_reviews": lead.get("reviews"),
        "website_status": lead.get("website_status"),
        "website": lead.get("website"),
        "audit": {k: audit.get(k) for k in ("issues", "load_seconds", "mobile_score", "builder", "title")}
        if audit
        else None,
    }
    lang = "Spanish (Puerto Rico)" if language == "es" else "English"
    response = client.beta.messages.parse(
        model=MODEL,
        max_tokens=4000,
        system=SYSTEM,
        output_config={"effort": "medium"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_format=Outreach,
        messages=[
            {
                "role": "user",
                "content": f"Write the outreach in {lang} for this lead:\n\n{json.dumps(facts, ensure_ascii=False, indent=2)}",
            }
        ],
    )
    if response.stop_reason == "refusal" or response.parsed_output is None:
        raise RuntimeError(f"Claude declined or returned no output for {lead.get('name')}")
    return response.parsed_output


def signature(language: str = "es") -> str:
    """CAN-SPAM applies in Puerto Rico: real sender, physical address, and an opt-out."""
    name = os.environ.get("SENDER_NAME", "Bengal Media PR")
    address = os.environ.get("SENDER_ADDRESS", "[DIRECCIÓN POSTAL FÍSICA REQUERIDA]")
    if language == "es":
        optout = "Si prefiere no recibir más correos, responda \"no gracias\" y no le escribo más."
    else:
        optout = "If you'd rather not hear from me again, just reply \"no thanks\"."
    return f"\n\n{name}\nBengal Media PR · bengalmediapr.com\n{address}\n\n{optout}"
