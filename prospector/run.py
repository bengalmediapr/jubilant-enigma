"""Leads -> audit -> outreach pipeline for Puerto Rico.

Examples:
  python -m prospector.run leads --category "restaurantes" --municipio Ponce Mayagüez
  python -m prospector.run audit
  python -m prospector.run outreach --limit 25
  python -m prospector.run all --category "dentistas" --municipio Bayamón Caguas

Each step reads and writes CSV files in ./data so you can review or edit them
in Excel/Google Sheets between steps. Nothing is ever sent automatically.
"""

import argparse
import csv
import json
import os
from pathlib import Path

DATA = Path("data")
LEADS_CSV = DATA / "leads.csv"
AUDITS_CSV = DATA / "audits.csv"
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


def cmd_leads(args) -> None:
    from prospector.leads import search

    existing = {row["place_id"]: row for row in read_csv(LEADS_CSV)}
    for municipio in args.municipio or DEFAULT_MUNICIPIOS:
        for category in args.category:
            found = search(category, municipio, max_pages=args.pages)
            new = [lead for lead in found if lead["place_id"] not in existing]
            existing.update({lead["place_id"]: lead for lead in new})
            print(f"{category} / {municipio}: {len(found)} found, {len(new)} new")
    rows = list(existing.values())
    write_csv(LEADS_CSV, rows)
    counts = {s: sum(r["website_status"] == s for r in rows) for s in ("none", "social_only", "has_site")}
    print(f"\n{len(rows)} leads in {LEADS_CSV}: {counts['none']} without a website, "
          f"{counts['social_only']} social-only, {counts['has_site']} with a site to audit")


def cmd_audit(args) -> None:
    from prospector.audit import audit

    done = {row["place_id"] for row in read_csv(AUDITS_CSV)}
    rows = read_csv(AUDITS_CSV)
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


def cmd_outreach(args) -> None:
    import anthropic

    from prospector.outreach import signature, write_outreach

    client = anthropic.Anthropic()
    audits = {row["place_id"]: row for row in read_csv(AUDITS_CSV)}
    done = {row["place_id"] for row in read_csv(OUTREACH_CSV)}
    rows = read_csv(OUTREACH_CSV)

    candidates = []
    for lead in read_csv(LEADS_CSV):
        if lead["place_id"] in done:
            continue
        audit_row = audits.get(lead["place_id"])
        if lead["website_status"] == "has_site":
            # Only pitch sites with real problems; a good site is a bad lead.
            if not audit_row or int(audit_row["issue_count"]) < args.min_issues:
                continue
        candidates.append((lead, audit_row))
    # Established businesses (many reviews) can afford a website: contact them first.
    candidates.sort(key=lambda c: -int(c[0].get("reviews") or 0))

    for i, (lead, audit_row) in enumerate(candidates[: args.limit], 1):
        audit_data = json.loads(audit_row["audit_json"]) if audit_row else None
        try:
            msg = write_outreach(client, lead, audit_data, language=args.language)
        except Exception as exc:  # keep going; one bad lead shouldn't stop the batch
            print(f"[{i}] {lead['name']}: skipped ({exc})")
            continue
        print(f"[{i}/{min(len(candidates), args.limit)}] {lead['name']}: {msg.subject}")
        rows.append({
            "place_id": lead["place_id"],
            "name": lead["name"],
            "municipio": lead["municipio"],
            "phone": lead["phone"],
            "email": (audit_row or {}).get("emails", "").split(", ")[0],
            "website": lead["website"],
            "website_status": lead["website_status"],
            "subject": msg.subject,
            "email_body": msg.email_body + signature(args.language),
            "whatsapp_message": msg.whatsapp_message,
            "top_issues": " | ".join(msg.top_issues),
            "status": "review",  # change to "approved" after you read it
        })
        write_csv(OUTREACH_CSV, rows)
    print(f"\nDrafts saved to {OUTREACH_CSV}. Review every one before sending.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("leads", "audit", "outreach", "all"):
        p = sub.add_parser(name)
        p.add_argument("--category", nargs="+", default=["restaurantes"],
                       help='Spanish search terms, e.g. "dentistas" "talleres de mecánica"')
        p.add_argument("--municipio", nargs="+", help="Default: the 12 largest municipios")
        p.add_argument("--pages", type=int, default=3, help="Google pages per search (20 results each)")
        p.add_argument("--limit", type=int, default=50, help="Max leads to audit / write per run")
        p.add_argument("--min-issues", type=int, default=2, help="Skip sites with fewer issues than this")
        p.add_argument("--language", choices=["es", "en"], default="es")
    args = parser.parse_args()

    if args.cmd in ("leads", "all"):
        cmd_leads(args)
    if args.cmd in ("audit", "all"):
        cmd_audit(args)
    if args.cmd in ("outreach", "all"):
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("Note: ANTHROPIC_API_KEY is not set; using any saved `ant auth login` profile.")
        cmd_outreach(args)


if __name__ == "__main__":
    main()
