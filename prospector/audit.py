"""Audit a business website and list concrete, sellable problems.

Every issue is phrased so it can be quoted back to the owner in outreach
("your site has no mobile layout") rather than as a technical score.
"""

import datetime
import os
import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

PSI_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
UA = "Mozilla/5.0 (compatible; BengalMediaPR-SiteAudit/1.0; +https://bengalmediapr.com)"
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
IGNORED_EMAIL_PARTS = ("sentry", "wixpress", "example.", "@2x", ".png", ".jpg", ".webp", "godaddy")
BUILDERS = {
    "wix.com": "Wix",
    "wixstatic": "Wix",
    "squarespace": "Squarespace",
    "godaddy": "GoDaddy Website Builder",
    "wp-content": "WordPress",
    "weebly": "Weebly",
    "shopify": "Shopify",
}


def audit(url: str) -> dict:
    result = {"url": url, "reachable": False, "issues": [], "emails": [], "socials": []}
    if not url.startswith("http"):
        url = "http://" + url
    try:
        start = time.monotonic()
        resp = requests.get(url, headers={"User-Agent": UA}, timeout=20, allow_redirects=True)
        elapsed = time.monotonic() - start
    except requests.exceptions.SSLError:
        result["issues"].append("El certificado de seguridad (SSL) está roto: el navegador muestra 'No seguro'")
        return result
    except requests.RequestException:
        result["issues"].append("El sitio web no carga o está caído")
        return result

    result["reachable"] = resp.ok
    result["final_url"] = resp.url
    result["load_seconds"] = round(elapsed, 2)
    result["page_kb"] = round(len(resp.content) / 1024)
    if not resp.ok:
        result["issues"].append(f"El sitio responde con error {resp.status_code}")
        return result

    html = resp.text
    soup = BeautifulSoup(html, "html.parser")
    issues = result["issues"]

    if not resp.url.startswith("https://"):
        issues.append("No usa HTTPS: Chrome marca el sitio como 'No seguro'")
    if not soup.find("meta", attrs={"name": "viewport"}):
        issues.append("No está optimizado para celulares (falta diseño responsive)")
    if elapsed > 3:
        issues.append(f"Carga lento: el servidor tardó {elapsed:.1f}s en responder")
    if len(resp.content) > 3 * 1024 * 1024:
        issues.append(f"La página pesa {result['page_kb']} KB, demasiado para datos móviles")

    title = soup.title.get_text(strip=True) if soup.title else ""
    result["title"] = title
    if not title:
        issues.append("No tiene título de página (malo para Google)")
    elif len(title) < 15:
        issues.append(f"El título de la página es muy genérico: \"{title}\"")
    desc = soup.find("meta", attrs={"name": "description"})
    if not desc or not desc.get("content", "").strip():
        issues.append("No tiene meta descripción: Google inventa el texto que aparece en búsquedas")
    if not soup.find("h1"):
        issues.append("No tiene encabezado principal (H1), lo que debilita el SEO")
    images = soup.find_all("img")
    missing_alt = [img for img in images if not img.get("alt")]
    if images and len(missing_alt) / len(images) > 0.5:
        issues.append(f"{len(missing_alt)} de {len(images)} imágenes no tienen texto alternativo")
    if not soup.find("script", attrs={"type": "application/ld+json"}):
        issues.append("No tiene datos estructurados de negocio local (Schema.org)")

    years = [int(y) for y in re.findall(r"(?:©|&copy;|copyright)\s*(?:\d{4}\s*[-–]\s*)?(\d{4})", html, re.I)]
    this_year = datetime.date.today().year
    if years and max(years) < this_year - 1:
        issues.append(f"El copyright dice {max(years)}: el sitio parece abandonado")

    lower = html.lower()
    result["builder"] = next((name for marker, name in BUILDERS.items() if marker in lower), "")
    if "flash" in lower and ".swf" in lower:
        issues.append("Usa Flash, que ningún navegador moderno muestra")
    if "<table" in lower and lower.count("<table") > 5 and not soup.find("meta", attrs={"name": "viewport"}):
        issues.append("Diseño antiguo basado en tablas")

    result["emails"] = _find_emails(html, soup, resp.url)
    result["socials"] = sorted(
        {a["href"] for a in soup.find_all("a", href=True) if re.search(r"facebook\.com|instagram\.com", a["href"])}
    )[:4]

    psi = pagespeed(resp.url)
    if psi is not None:
        result["mobile_score"] = psi
        if psi < 50:
            issues.append(f"Google le da {psi}/100 en velocidad móvil (PageSpeed)")
    return result


def _find_emails(html: str, soup: BeautifulSoup, base_url: str) -> list[str]:
    emails = set(EMAIL_RE.findall(html))
    for a in soup.find_all("a", href=True):
        if a["href"].lower().startswith("mailto:"):
            emails.add(a["href"][7:].split("?")[0])
    if not emails:
        # Try one contact page; most small business sites put the email there.
        for a in soup.find_all("a", href=True):
            if re.search(r"contact|contacto", a["href"], re.I):
                try:
                    page = requests.get(urljoin(base_url, a["href"]), headers={"User-Agent": UA}, timeout=15)
                    emails.update(EMAIL_RE.findall(page.text))
                except requests.RequestException:
                    pass
                break
    domain = urlparse(base_url).netloc.removeprefix("www.")
    clean = [e.lower().strip(".") for e in emails if not any(p in e.lower() for p in IGNORED_EMAIL_PARTS)]
    # Emails on the business's own domain first.
    return sorted(set(clean), key=lambda e: (not e.endswith(domain), e))[:3]


def pagespeed(url: str) -> int | None:
    key = os.environ.get("PAGESPEED_API_KEY")
    if not key:
        return None
    try:
        resp = requests.get(
            PSI_URL,
            params={"url": url, "strategy": "mobile", "category": "performance", "key": key},
            timeout=90,
        )
        resp.raise_for_status()
        score = resp.json()["lighthouseResult"]["categories"]["performance"]["score"]
        return round(score * 100)
    except (requests.RequestException, KeyError, TypeError):
        return None
