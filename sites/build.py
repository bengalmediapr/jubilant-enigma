"""Build bilingual static websites for Puerto Rico businesses from industry templates.

Examples:
  python -m sites.build demo                       # all 10 industry demos + gallery in dist/
  python -m sites.build demo dentista taller       # just these
  python -m sites.build client sites/clients/ejemplo-dentista.json
  python -m sites.build lead "Clínica Dental" --industry dentista   # mockup from data/leads.csv

Output is plain HTML/CSS in dist/<slug>/, ready for Cloudflare Pages:
  npx wrangler pages deploy dist/<slug> --project-name <slug>
"""

import argparse
import copy
import csv
import datetime
import json
import re
import shutil
import unicodedata
from pathlib import Path
from urllib.parse import quote, quote_plus

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
INDUSTRIES = ROOT / "industries"
ICONS = ROOT / "icons"
DIST = Path("dist")
LEADS_CSV = Path("data/leads.csv")

# Words in a Google Maps category or search term -> industry template.
INDUSTRY_KEYWORDS = {
    "barberia": ["barber"],
    "unas": ["uñas", "unas", "nail"],
    "foodtruck": ["food truck", "foodtruck", "burger", "smash"],
    "dentista": ["dent", "ortodon", "odonto"],
    "quiropractico": ["quiropr", "chiropr", "terapia física", "physical therap"],
    "medico": ["médic", "medic", "clínica", "clinic", "doctor", "pediatr", "salud", "health"],
    "abogado": ["abogad", "notari", "lawyer", "attorney", "legal", "bufete"],
    "contador": ["contador", "contab", "cpa", "account", "tax", "planilla"],
    "taller": ["taller", "mecánic", "mechanic", "auto repair", "gomera", "car repair", "hojalater"],
    "solar": ["solar", "placa", "contratist", "contractor", "techo", "roof", "electric"],
    "salon": ["salón", "salon", "barber", "belleza", "beauty", "uñas", "nail", "spa"],
    "restaurante": ["restaur", "café", "cafe", "comida", "food", "bar", "panader", "bakery", "pizz"],
    "alquiler": ["alquiler", "rental", "hospeda", "lodging", "guest", "villa", "airbnb", "hotel"],
}

UI = {
    "es": {
        "lang_switch": "English", "nav": {
            "services": "Servicios", "menu": "Menú", "about": "Nosotros", "steps": "Cómo trabajamos",
            "insurance": "Planes", "gallery": "Galería", "faq": "Preguntas", "contact": "Contacto",
            "testimonials": "Reseñas",
        },
        "hours": "Horario", "address": "Dirección", "phone": "Teléfono", "call": "Llamar",
        "whatsapp": "WhatsApp", "directions": "Cómo llegar", "reviews": "reseñas en Google",
        "form_name": "Su nombre", "form_message": "¿En qué le podemos ayudar?",
        "form_send": "Enviar por WhatsApp", "form_send_email": "Enviar por email",
        "menu_toggle": "Abrir menú", "rights": "Todos los derechos reservados.",
        "made_by": "Sitio web por", "open_whatsapp": "Escríbanos por WhatsApp",
        "photo_placeholder": "Foto",
    },
    "en": {
        "lang_switch": "Español", "nav": {
            "services": "Services", "menu": "Menu", "about": "About", "steps": "How it works",
            "insurance": "Insurance", "gallery": "Gallery", "faq": "FAQ", "contact": "Contact",
            "testimonials": "Reviews",
        },
        "hours": "Hours", "address": "Address", "phone": "Phone", "call": "Call",
        "whatsapp": "WhatsApp", "directions": "Directions", "reviews": "Google reviews",
        "form_name": "Your name", "form_message": "How can we help?",
        "form_send": "Send on WhatsApp", "form_send_email": "Send by email",
        "menu_toggle": "Open menu", "rights": "All rights reserved.",
        "made_by": "Website by", "open_whatsapp": "Message us on WhatsApp",
        "photo_placeholder": "Photo",
    },
}

NAV_SECTIONS = ["services", "menu", "about", "steps", "insurance", "gallery", "testimonials", "faq", "contact"]


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:50] or "sitio"


def deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        elif value not in (None, ""):
            out[key] = copy.deepcopy(value)
    return out


def fill(value, tokens: dict):
    """Replace {name}, {municipio}, ... inside every string of the content tree."""
    if isinstance(value, str):
        return re.sub(r"\{(\w+)\}", lambda m: str(tokens.get(m.group(1), m.group(0))), value)
    if isinstance(value, list):
        return [fill(v, tokens) for v in value]
    if isinstance(value, dict):
        return {k: fill(v, tokens) for k, v in value.items()}
    return value


def load_industry(key: str) -> dict:
    path = INDUSTRIES / f"{key}.json"
    if not path.exists():
        names = ", ".join(sorted(p.stem for p in INDUSTRIES.glob("*.json")))
        raise SystemExit(f"Unknown industry '{key}'. Choose one of: {names}")
    return json.loads(path.read_text(encoding="utf-8"))


def detect_industry(*texts: str) -> str | None:
    blob = " ".join(texts).lower()
    for key, words in INDUSTRY_KEYWORDS.items():
        if any(w in blob for w in words):
            return key
    return None


def icon(name: str, size: int = 24) -> str:
    path = ICONS / f"{name}.svg"
    if not path.exists():
        path = ICONS / "check.svg"
    svg = path.read_text(encoding="utf-8")
    svg = re.sub(r"<!--.*?-->\s*", "", svg, flags=re.S)
    svg = re.sub(r'class="[^"]*"', 'class="icon" aria-hidden="true"', svg, count=1)
    svg = re.sub(r'width="24"', f'width="{size}"', svg, count=1)
    return re.sub(r'height="24"', f'height="{size}"', svg, count=1)


def fonts_url(theme: dict) -> str:
    families = []
    for font, weights in ((theme["font_head"], theme.get("head_weights", "600;700")),
                          (theme["font_body"], "400;500;600;700")):
        family = f"family={quote_plus(font)}:wght@{weights}"
        if family not in families:
            families.append(family)
    return "https://fonts.googleapis.com/css2?" + "&".join(families) + "&display=swap"


def build_site(site: dict, out_dir: Path, explicit_index: bool = False) -> Path:
    """explicit_index links to .../index.html, for hosts that don't serve folder URLs."""
    site = copy.deepcopy(site)
    site.setdefault("slug", slugify(site["name"]))
    phone_digits = re.sub(r"\D", "", site.get("phone", ""))
    if len(phone_digits) == 10:
        phone_digits = "1" + phone_digits
    site["phone_link"] = f"+{phone_digits}" if phone_digits else ""
    whatsapp = re.sub(r"\D", "", site.get("whatsapp", "")) or (phone_digits if site.get("whatsapp_from_phone", True) else "")
    site["whatsapp"] = whatsapp
    site["map_query"] = site.get("map_query") or ", ".join(
        x for x in (site["name"], site.get("address"), site.get("municipio"), "Puerto Rico") if x)
    site["year"] = datetime.date.today().year
    tokens = {k: site.get(k, "") for k in ("name", "municipio", "phone", "address", "email")}
    site["content"] = fill(site["content"], tokens)

    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape(["html", "j2"]))
    env.globals.update(icon=icon, quote=quote, quote_plus=quote_plus)
    page = env.get_template("page.html.j2")

    if out_dir.exists():
        shutil.rmtree(out_dir)
    (out_dir / "en").mkdir(parents=True)
    base_url = f"https://{site['domain']}" if site.get("domain") else ""
    for lang in ("es", "en"):
        content = site["content"][lang]
        sections = [s for s in site["sections"] if s == "hero" or _has_content(s, content, site)]
        nav = [s for s in NAV_SECTIONS if s in sections and s != "contact"]
        html = page.render(
            site=site, c=content, ui=UI[lang], lang=lang, sections=sections, nav=nav,
            theme=site["theme"], fonts_url=fonts_url(site["theme"]), base_url=base_url,
            prefix="" if lang == "es" else "../", other_href=("en/" if lang == "es" else "../") + ("index.html" if explicit_index else ""),
            home_href="index.html" if explicit_index else "./",
            back_href=("../index.html" if lang == "es" else "../../index.html") if explicit_index else "",
            schema=json.dumps(_schema(site, base_url), ensure_ascii=False),
        )
        target = out_dir / ("index.html" if lang == "es" else "en/index.html")
        target.write_text(html, encoding="utf-8")

    for asset in ("site.css", "site.js"):
        shutil.copy(ROOT / "static" / asset, out_dir / asset)
    (out_dir / "favicon.svg").write_text(_favicon(site), encoding="utf-8")
    if site.get("assets_dir"):
        shutil.copytree(Path(site["assets_dir"]), out_dir / "images", dirs_exist_ok=True)
    (out_dir / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n" + (f"Sitemap: {base_url}/sitemap.xml\n" if base_url else ""), encoding="utf-8")
    if base_url:
        (out_dir / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"  <url><loc>{base_url}/</loc></url>\n  <url><loc>{base_url}/en/</loc></url>\n</urlset>\n",
            encoding="utf-8")
    return out_dir


def _has_content(section: str, content: dict, site: dict) -> bool:
    if section == "testimonials":
        return bool(site.get("testimonials"))  # only real reviews, never invented ones
    if section == "contact":
        return True
    return bool(content.get(section))


def _schema(site: dict, base_url: str) -> dict:
    schema = {
        "@context": "https://schema.org",
        "@type": site.get("schema_type", "LocalBusiness"),
        "name": site["name"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": site.get("address", ""),
            "addressLocality": site.get("municipio", ""),
            "addressRegion": "PR",
            "addressCountry": "US",
        },
    }
    if site.get("phone"):
        schema["telephone"] = site["phone_link"]
    if base_url:
        schema["url"] = base_url + "/"
    if site.get("email"):
        schema["email"] = site["email"]
    same_as = [v for v in site.get("social", {}).values() if v]
    if same_as:
        schema["sameAs"] = same_as
    if site.get("schema_extra"):
        schema.update(site["schema_extra"])
    return schema


def _favicon(site: dict) -> str:
    letter = site["name"].strip()[:1].upper() or "B"
    t = site["theme"]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" '
            f'fill="{t["primary"]}"/><text x="32" y="44" font-family="Arial, sans-serif" font-size="34" '
            f'font-weight="700" fill="{t["primary_ink"]}" text-anchor="middle">{letter}</text></svg>')


def site_for(industry_key: str, client: dict | None = None) -> dict:
    industry = load_industry(industry_key)
    demo = industry.pop("demo", {})
    if client:
        # A real business never inherits the demo's sample address, phone or rating,
        # and only shows hours when the client file lists them.
        industry.pop("hours", None)
        site = deep_merge(industry, client)
        site["is_demo"] = False
    else:
        site = deep_merge(industry, demo)
        site["is_demo"] = True
    site["industry"] = industry_key
    return site


def cmd_demo(args) -> None:
    keys = args.industries or sorted(p.stem for p in INDUSTRIES.glob("*.json"))
    built = []
    for key in keys:
        site = site_for(key)
        out = build_site(site, DIST / f"demo-{key}", explicit_index=args.preview)
        built.append((key, site))
        print(f"{key:14} -> {out}/index.html")
    _gallery(built)
    print(f"\nGallery: {DIST}/index.html")


def cmd_client(args) -> None:
    client = json.loads(Path(args.path).read_text(encoding="utf-8"))
    key = client.get("industry") or args.industry
    if not key:
        raise SystemExit('Add "industry": "<name>" to the client file or pass --industry')
    site = site_for(key, client)
    out = build_site(site, DIST / site.get("slug", slugify(site["name"])))
    print(f"Built {out}/index.html\nDeploy: npx wrangler pages deploy {out} --project-name {out.name}")


def cmd_previews(args) -> None:
    """Build every client file marked "preview": true into dist/previews/<slug>/ (one Cloudflare project)."""
    root = DIST / "previews"
    built = []
    for path in sorted((ROOT / "clients").glob("*.json")):
        client = json.loads(path.read_text(encoding="utf-8"))
        if not client.get("preview"):
            continue
        site = site_for(client["industry"], client)
        site.setdefault("noindex", True)
        site.setdefault("preview_banner", True)
        slug = site.get("slug") or slugify(site["name"])
        build_site(site, root / slug, explicit_index=args.explicit_index)
        built.append(slug)
        print(f"{site['name']:32} -> {root / slug}/")
    print(f"\n{len(built)} previews. Deploy all at once:\n  npx wrangler pages deploy {root} --project-name bengal-previews"
          f"\nEach one is then at https://bengal-previews.pages.dev/<slug>/")


def cmd_lead(args) -> None:
    if not LEADS_CSV.exists():
        raise SystemExit(f"{LEADS_CSV} not found. Run the prospector first or use `client`.")
    with LEADS_CSV.open(encoding="utf-8") as f:
        leads = list(csv.DictReader(f))
    query = args.query.lower()
    matches = [l for l in leads if query in l["name"].lower() or query == l.get("place_id", "").lower()]
    if not matches:
        raise SystemExit(f"No lead matching '{args.query}' in {LEADS_CSV}")
    for lead in matches[: args.max]:
        key = args.industry or detect_industry(lead.get("category", ""), lead.get("type", ""), lead["name"])
        if not key:
            print(f"Skipping {lead['name']}: can't tell the industry, pass --industry")
            continue
        client = {
            "industry": key,
            "name": lead["name"],
            "municipio": lead.get("municipio", ""),
            "address": lead.get("address", "").replace(", Puerto Rico", ""),
            "phone": lead.get("phone", ""),
            "rating": float(lead["rating"]) if lead.get("rating") else None,
            "reviews": int(lead["reviews"]) if lead.get("reviews") else None,
            "map_query": lead.get("address") or "",
            "noindex": True,  # mockup preview; remove once the client approves and you add their domain
        }
        slug = slugify(lead["name"])
        client_path = ROOT / "clients" / f"{slug}.json"
        client_path.parent.mkdir(exist_ok=True)
        if not client_path.exists():  # never overwrite edits you made to a client file
            client_path.write_text(json.dumps(client, ensure_ascii=False, indent=2), encoding="utf-8")
        client = json.loads(client_path.read_text(encoding="utf-8"))
        site = site_for(client["industry"], client)
        out = build_site(site, DIST / slug)
        print(f"{lead['name']} ({key}) -> {out}/index.html  [edit {client_path} and rebuild with `client`]")


def _gallery(built: list[tuple[str, dict]]) -> None:
    cards = "\n".join(
        f'<a class="card" href="demo-{key}/" style="--p:{s["theme"]["primary"]};--a:{s["theme"]["accent"]}">'
        f'<span class="swatch"></span><strong>{s["label"]["es"]}</strong><small>{s["label"]["en"]} · {s["name"]}</small></a>'
        for key, s in built)
    (DIST / "index.html").write_text(f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Plantillas · Bengal Media PR</title>
<style>body{{font-family:system-ui,sans-serif;margin:0;padding:32px 16px;background:#f6f5f2;color:#1c1c1c}}
main{{max-width:960px;margin:auto}}h1{{margin:0 0 4px}}p{{color:#555;margin:0 0 24px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}}
.card{{display:flex;flex-direction:column;gap:4px;padding:18px;border-radius:14px;background:#fff;text-decoration:none;color:inherit;box-shadow:0 1px 3px #0001}}
.card:hover{{box-shadow:0 6px 20px #0002}}.swatch{{height:56px;border-radius:10px;margin-bottom:8px;background:linear-gradient(120deg,var(--p) 60%,var(--a) 60%)}}
small{{color:#666}}</style></head><body><main><h1>Plantillas por industria</h1>
<p>Bengal Media PR · demos bilingües listas para personalizar</p><div class="grid">{cards}</div></main></body></html>""",
        encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("demo", help="Build demo sites for industries")
    p.add_argument("industries", nargs="*")
    p.add_argument("--preview", action="store_true", help="Link to index.html files explicitly (for static previews)")
    p = sub.add_parser("client", help="Build a client site from a JSON file")
    p.add_argument("path")
    p.add_argument("--industry")
    p = sub.add_parser("previews", help="Build all client previews into dist/previews/")
    p.add_argument("--explicit-index", action="store_true", help="Link to index.html files explicitly")
    p = sub.add_parser("lead", help="Build a mockup for a lead in data/leads.csv")
    p.add_argument("query", help="Part of the business name, or its place_id")
    p.add_argument("--industry")
    p.add_argument("--max", type=int, default=1, help="Build up to this many matching leads")
    args = parser.parse_args()
    {"demo": cmd_demo, "client": cmd_client, "lead": cmd_lead, "previews": cmd_previews}[args.cmd](args)


if __name__ == "__main__":
    main()
