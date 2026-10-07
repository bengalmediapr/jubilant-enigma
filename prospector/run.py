"""Leads -> audit -> outreach pipeline for Puerto Rico.

Examples:
  python -m prospector.run leads --category "restaurantes" --municipio Ponce Mayagüez   (Google Places key)
  python -m prospector.run add --name "Taller Ortiz" --category talleres --municipio Bayamón --phone 787-555-0000
  python -m prospector.run audit
  python -m prospector.run queue --limit 10      # then /outreach in Claude Code writes the drafts
  python -m prospector.run export                # drafts -> data/outreach.csv with signature

Each step reads and writes files in ./data so you can review or edit them in
Excel/Google Sheets between steps. Nothing is ever sent automatically.
"""

import argparse
import csv
import hashlib
import json
import os
import unicodedata
from pathlib import Path

DATA = Path("data")
LEADS_CSV = DATA / "leads.csv"
AUDITS_CSV = DATA / "audits.csv"
QUEUE_JSON = DATA / "outreach_queue.json"
DRAFTS = DATA / "drafts"
OUTREACH_CSV = DATA / "outreach.csv"

# Largest metro areas first; pass --municipio to target others.
DEFAULT_MUNICIPIOS = [
    "San Juan", "Bayamón", "Carolina", "Ponce", "Caguas", "Guaynabo",
    "Arecibo", "Toa Baja", "Mayagüez", "Trujillo Alto", "Dorado", "Humacao",
]


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> None:
    DATA.mkdir(exist_ok=True)
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _key(name: str, municipio: str) -> str:
    text = unicodedata.normalize("NFKD", f"{name}|{municipio}").encode("ascii", "ignore").decode().lower()
    return "".join(ch for ch in text if ch.isalnum() or ch == "|")


def cmd_leads(args) -> None:
    from prospector.leads import search

    existing = {row["place_id"]: row for row in read_csv(LEADS_CSV)}
    for municipio in args.municipio or DEFAULT_MUNICIPIOS:
        for category in args.category:
            found = search(category, municipio, max_pages=args.pages)
            new = [lead for lead in found if lead["place_id"] not in existing]
            existing.update({lead["place_id"]: lead for lead in new})
            print(f"{category} / {municipio}: {len(found)} found, {len(new)} new")
    write_csv(LEADS_CSV, list(existing.values()))
    cmd_stats(args)


def cmd_add(args) -> None:
    from prospector.leads import SOCIAL_HOSTS

    rows = read_csv(LEADS_CSV)
    key = _key(args.name, args.municipio)
    if any(_key(r["name"], r.get("municipio", "")) == key for r in rows):
        print(f"Already in leads: {args.name} ({args.municipio})")
        return
    website = (args.website or "").strip()
    if not website:
        status = "none"
    elif any(host in website.lower() for host in SOCIAL_HOSTS):
        status = "social_only"
    else:
        status = "has_site"
    rows.append({
        "place_id": "m-" + hashlib.sha1(key.encode()).hexdigest()[:12],
        "name": args.name,
        "category": args.category[0] if args.category else "",
        "type": "",
        "municipio": args.municipio,
        "address": args.address or "",
        "phone": args.phone or "",
        "phone_intl": "",
        "website": website,
        "website_status": status,
        "rating": args.rating or "",
        "reviews": args.reviews or 0,
        "maps_url": "",
    })
    write_csv(LEADS_CSV, rows)
    print(f"Added {args.name} ({status})")


def cmd_stats(args) -> None:
    rows = read_csv(LEADS_CSV)
    counts = {s: sum(r["website_status"] == s for r in rows) for s in ("none", "social_only", "has_site")}
    print(f"{len(rows)} leads in {LEADS_CSV}: {counts['none']} without a website, "
          f"{counts['social_only']} social-only, {counts['has_site']} with a site to audit")
    if AUDITS_CSV.exists():
        print(f"{len(read_csv(AUDITS_CSV))} audited; {len(list(DRAFTS.glob('*.json')))} drafts written")


def cmd_audit(args) -> None:
    from prospector.audit import audit

    rows = read_csv(AUDITS_CSV)
    done = {row["place_id"] for row in rows}
    todo = [l for l in read_csv(LEADS_CSV) if l["website_status"] == "has_site" and l["place_id"] not in done]
    for i, lead in enumerate(todo[: args.limit], 1):
        result = audit(lead["website"])
        print(f"[{i}/{min(len(todo), args.limit)}] {lead['name']}: {len(result['issues'])} issues")
        rows.append({
            "place_id": lead["place_id"],
            "name": lead["name"],
            "website": lead["website"],
            "issue_count": len(result["issues"]),
            "issues": " | ".join(result["issues"]),
            "emails": ", ".join(result["emails"]),
            "load_seconds": result.get("load_seconds", ""),
            "mobile_score": result.get("mobile_score", ""),
            "builder": result.get("builder", ""),
            "audit_json": json.dumps(result, ensure_ascii=False),
        })
        write_csv(AUDITS_CSV, rows)  # save as we go so a crash loses nothing
    print(f"\nAudits saved to {AUDITS_CSV}")


def cmd_queue(args) -> None:
    """Pick the next leads worth pitching and save them, with audit facts, for /outreach."""
    audits = {row["place_id"]: row for row in read_csv(AUDITS_CSV)}
    drafted = {p.stem for p in DRAFTS.glob("*.json")}
    queue = []
    for lead in read_csv(LEADS_CSV):
        if lead["place_id"] in drafted:
            continue
        audit_row = audits.get(lead["place_id"])
        if lead["website_status"] == "has_site":
            # Only pitch sites with real problems; a good site is a bad lead.
            if not audit_row or int(audit_row["issue_count"]) < args.min_issues:
                continue
        audit = json.loads(audit_row["audit_json"]) if audit_row else None
        queue.append({
            "place_id": lead["place_id"],
            "business": lead["name"],
            "category": lead.get("type") or lead.get("category"),
            "municipio": lead.get("municipio"),
            "google_rating": lead.get("rating"),
            "google_reviews": lead.get("reviews"),
            "website_status": lead["website_status"],
            "website": lead.get("website"),
            "channel": "email" if audit and audit.get("emails") else "whatsapp/phone",
            "audit": {k: audit.get(k) for k in ("issues", "load_seconds", "mobile_score", "builder", "title")}
            if audit else None,
        })
    # Established businesses (many reviews) can afford a website: contact them first.
    queue.sort(key=lambda q: -int(q["google_reviews"] or 0))
    queue = queue[: args.limit]
    DATA.mkdir(exist_ok=True)
    QUEUE_JSON.write_text(json.dumps({"language": args.language, "leads": queue}, ensure_ascii=False, indent=2),
                          encoding="utf-8")
    print(f"{len(queue)} leads queued in {QUEUE_JSON}. Write drafts to {DRAFTS}/<place_id>.json")


def signature(language: str = "es") -> str:
    """CAN-SPAM applies in Puerto Rico: real sender, physical address, and an opt-out."""
    name = os.environ.get("SENDER_NAME", "Bengal Media PR")
    address = os.environ.get("SENDER_ADDRESS", "[DIRECCIÓN POSTAL FÍSICA REQUERIDA]")
    if language == "es":
        optout = "Si prefiere no recibir más correos, responda \"no gracias\" y no le escribo más."
    else:
        optout = "If you'd rather not hear from me again, just reply \"no thanks\"."
    return f"\n\n{name}\nBengal Media PR · bengalmediapr.com\n{address}\n\n{optout}"


def cmd_export(args) -> None:
    leads = {row["place_id"]: row for row in read_csv(LEADS_CSV)}
    audits = {row["place_id"]: row for row in read_csv(AUDITS_CSV)}
    rows = {row["place_id"]: row for row in read_csv(OUTREACH_CSV)}
    added = 0
    for path in sorted(DRAFTS.glob("*.json")):
        if path.stem in rows:
            continue  # keep any status/edits already made in the CSV
        draft = json.loads(path.read_text(encoding="utf-8"))
        lead = leads.get(path.stem, {})
        lang = draft.get("language", "es")
        rows[path.stem] = {
            "place_id": path.stem,
            "name": lead.get("name", ""),
            "municipio": lead.get("municipio", ""),
            "phone": lead.get("phone", ""),
            "email": audits.get(path.stem, {}).get("emails", "").split(", ")[0],
            "website": lead.get("website", ""),
            "website_status": lead.get("website_status", ""),
            "subject": draft["subject"],
            "email_body": draft["email_body"].rstrip() + signature(lang),
            "whatsapp_message": draft["whatsapp_message"],
            "top_issues": " | ".join(draft.get("top_issues", [])),
            "status": "review",  # change to "approved" after you read it
        }
        added += 1
    write_csv(OUTREACH_CSV, list(rows.values()))
    print(f"{added} new drafts added to {OUTREACH_CSV}. Review every one before sending.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("leads", "add", "stats", "audit", "queue", "export"):
        p = sub.add_parser(name)
        p.add_argument("--category", nargs="+", default=["restaurantes"],
                       help='Spanish search terms, e.g. "dentistas" "talleres de mecánica"')
        p.add_argument("--municipio", nargs="+" if name != "add" else None,
                       required=name == "add", help="Default: the 12 largest municipios")
        p.add_argument("--pages", type=int, default=3, help="Google pages per search (20 results each)")
        p.add_argument("--limit", type=int, default=50, help="Max leads to audit / queue per run")
        p.add_argument("--min-issues", type=int, default=2, help="Skip sites with fewer issues than this")
        p.add_argument("--language", choices=["es", "en"], default="es")
        if name == "add":
            p.add_argument("--name", required=True)
            p.add_argument("--phone")
            p.add_argument("--website")
            p.add_argument("--address")
            p.add_argument("--rating")
            p.add_argument("--reviews")
    args = parser.parse_args()
    {"leads": cmd_leads, "add": cmd_add, "stats": cmd_stats, "audit": cmd_audit,
     "queue": cmd_queue, "export": cmd_export}[args.cmd](args)


if __name__ == "__main__":
    main()
