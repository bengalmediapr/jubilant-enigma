# Bengal Media PR — Prospector + Site Templates

**Start here: [GUIA.md](GUIA.md)** (Spanish, 5 steps).

A Puerto Rico version of the "200 websites in 12 months" system:
**find local businesses → audit their websites → write personalized outreach → send a free mockup → build and host the site.**

There are no paid API keys. Claude Code does the writing and research inside this project through slash commands.

| Reel's stack | This repo | |
|---|---|---|
| Apollo (leads) | `/find-leads` (web search), or Google Places (optional key) | Google Maps covers PR's restaurants, clinics, talleres and salons. Apollo doesn't. |
| Swokei (site analysis + outreach) | `prospector/audit.py` + `/outreach` | Checks HTTPS, mobile, speed, SEO basics and abandoned sites, then writes Puerto Rican Spanish outreach quoting the real problems. |
| Claude Code (build sites) | `sites/`: 10 industry templates + `/mockup` | Bilingual, mobile-first, WhatsApp button, Google schema. |
| Cloudflare (hosting) | `npx wrangler pages deploy` | Free, fast, SSL included. |
| Soro (SEO blog) | Roadmap | |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env    # fill in SENDER_NAME and SENDER_ADDRESS
set -a; source .env; set +a
```

Open the folder in Claude Code, and the slash commands below become available.

## Daily workflow

```text
/find-leads dentistas Ponce Juana Díaz     1. Claude searches the web and adds real businesses to data/leads.csv
python -m prospector.run audit             2. checks every lead that has a website
/outreach 10                               3. Claude writes 10 drafts → data/outreach.csv (with legal footer)
/mockup "Clínica Dental X"                 4. Claude builds a homepage mockup customized with their real info
```

Open `data/outreach.csv` in Google Sheets, read each draft, and change `status` to `approved` before you send.
Nothing is ever sent automatically.

Other commands: `python -m prospector.run stats` shows lead counts, `add --name ... --municipio ...` adds a lead by hand, and
`leads --category ... --municipio ...` bulk-searches Google Maps if you set `GOOGLE_PLACES_API_KEY`.

## Website templates

![The 10 industry templates](docs/templates-preview.png)

```bash
python -m sites.build demo          # all 10 demos + a gallery page at dist/index.html
python -m sites.build lead "Café"   # mockup for a lead in data/leads.csv (writes sites/clients/<slug>.json)
python -m sites.build previews     # every client marked "preview": true -> dist/previews/<slug>/ (one Cloudflare project)
python -m sites.build client sites/clients/ejemplo-dentista.json   # a real client site
npx wrangler pages deploy dist/<slug> --project-name <slug>        # publish to Cloudflare Pages
python -m sites.export <slug>      # one client's site as its own git repo in exports/<slug>/
```

| Industry key | For | Look |
|---|---|---|
| `dentista` | Dentists | Teal, clean |
| `quiropractico` | Chiropractors, physical therapy (ACAA cases) | Sage and sand, calm serif |
| `medico` | Clinics and family doctors | Trust blue |
| `abogado` | Attorney-notaries | Navy and gold, dark hero |
| `contador` | CPAs (Hacienda, IVU, SURI, Act 60) | Deep green, editorial |
| `taller` | Auto repair (marbete prep) | Charcoal and orange, bold caps |
| `solar` | Solar, batteries, roof sealing, electricians | Navy and sun yellow |
| `salon` | Salons, barbershops, nails | Black and rose, pricelist |
| `restaurante` | Restaurants, cafés (menu section) | Terracotta, warm |
| `alquiler` | Vacation rentals, "book direct" | Turquoise and sand, gallery |
| `barberia` | Barbershops | Poster: huge name, barber-pole stripes, price board |
| `unas` | Nail salons | Poster: italic serif, glossy chrome, price card |
| `foodtruck` | Food trucks, burgers, quick food | Poster: loud yellow, hard shadows, "most ordered" board |

Every site comes in Spanish (`/`) and English (`/en/`). Each one includes a floating WhatsApp button, a contact form that opens WhatsApp (so there's no server to maintain), a Google Map, hours, a schema.org LocalBusiness entry, a sitemap, and a "Sitio web por Bengal Media PR" footer link.

**Customizing a client.** Copy `sites/clients/ejemplo-dentista.json`. Any key you add overrides the industry template: name, phone, hours, colors (`theme`), any text (`content.es.hero.title`), photos (`hero_image`, `gallery_images`, `assets_dir`), and real `testimonials`. Sections, colors and copy for each industry live in `sites/industries/<key>.json`.

**Honesty rules built in.** The testimonials section only appears when you add real reviews, so it never shows invented ones. Demo and mockup pages carry `noindex` so Google doesn't index them. Template prices and plan names are examples, so replace them with the client's real ones before launch.

## Puerto Rico playbook

**Niches with high-value clients who find customers on Google:** dentistas, quiroprácticos, clínicas, abogados-notarios, CPAs, talleres, solar and techos, salones and barberías, restaurantes, and alquileres vacacionales (Rincón, Isabela, Vieques, Culebra).

**Leads by `website_status`:**
1. `none`: no website. This is your biggest pool. Reach them by phone or WhatsApp, one at a time.
2. `social_only`: Facebook or Instagram only. Reach them by Instagram DM or WhatsApp.
3. `has_site`: pitched only when the audit finds 2 or more real problems. Reach them by email, using the address the audit found.

**Offer.** Keep it to one or two packages, for example a website in 7 days plus a monthly plan for hosting, updates, and Google Business Profile. The monthly plan is what builds steady income.

**Closing.** Run `/mockup`, deploy it, and send the preview link: *"Le preparé un ejemplo de cómo se vería su página."* Seeing their own business on a modern site closes far better than a proposal.

**Send safely:**
- **Don't send cold email from @bengalmediapr.com.** Use a look-alike domain with SPF, DKIM, and DMARC set up, warm it up for 2–3 weeks, and send at most 30–50 emails per inbox per day (Instantly or Smartlead can import `outreach.csv`).
- **CAN-SPAM applies in PR.** Every email needs your real name, a postal address (`SENDER_ADDRESS`; a PO box works), and an opt-out. Each draft gets these automatically, so honor opt-outs right away.
- **WhatsApp:** send messages by hand from a business number. Bulk-blasting gets the number banned.

## Roadmap

- [x] Leads → audit → personalized outreach
- [x] 10 bilingual industry templates + mockup builder
- [ ] Bilingual SEO blog on bengalmediapr.com ("diseño web en Puerto Rico", "páginas web para [industria] en [municipio]")
- [ ] Free "Analiza tu web" page on bengalmediapr.com that runs the audit and captures inbound leads
