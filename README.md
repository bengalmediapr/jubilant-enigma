# Bengal Media PR — Prospector

A Puerto Rico version of the "200 websites in 12 months" system:
**find local businesses → audit their websites → write personalized outreach → build the sites with Claude Code → host on Cloudflare.**

| Reel's stack | This repo / PR version | Why |
|---|---|---|
| Apollo (leads) | `prospector/leads.py` — Google Places API | Apollo barely covers PR restaurants, clinics, talleres, salones. Google Maps has all of them, plus whether they have a website. |
| Swokei (site analysis + outreach) | `prospector/audit.py` + `prospector/outreach.py` | Checks HTTPS, mobile, speed, SEO basics, abandoned sites; Claude writes the email in Puerto Rican Spanish quoting the real problems. |
| Soro (SEO blog) | Phase 3 below | Bilingual blog for bengalmediapr.com. |
| Claude Code (build sites) | This repo, later `sites/` | One template per industry, customized per client. |
| Cloudflare (hosting) | Cloudflare Pages | Free, fast, SSL included. |

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env        # fill in keys
set -a; source .env; set +a

# 1. Leads: dentists and restaurants in Ponce and Mayagüez
python -m prospector.run leads --category dentistas restaurantes --municipio Ponce Mayagüez

# 2. Audit every lead that has a website
python -m prospector.run audit --limit 100

# 3. Draft outreach (Spanish by default, --language en for English)
python -m prospector.run outreach --limit 25
```

Results go to `data/leads.csv`, `data/audits.csv`, and `data/outreach.csv`. Open them in Google Sheets.
**Nothing is sent automatically.** Read each draft, change `status` to `approved`, then send.

Keys you need:
- **Claude API key**: console.anthropic.com. Drafts cost a few cents each.
- **Google Places API key**: Google Cloud Console → enable "Places API (New)". There is a free monthly allowance, so check current pricing.
- *(optional)* **PageSpeed Insights API key**: free. It adds Google's real mobile speed score to each audit.

## The three kinds of leads

`leads.csv` sorts each business by `website_status`:

1. **`none`**: no website. This is your biggest pool in PR. Pitch: *"When people search for 'dentista en Ponce' on Google, they find your competitors."* Contact them by **phone or WhatsApp** (use `whatsapp_message`), because they rarely publish an email.
2. **`social_only`**: only Facebook or Instagram. Pitch: social pages don't show up on Google and can't take appointments or orders. Contact them by Instagram DM or WhatsApp.
3. **`has_site`**: the site gets audited, and only sites with 2 or more real problems get pitched. Contact them by email, using the address the audit found on their site.

Outreach is ordered by Google review count, so you contact established businesses, which can pay, first.

## Puerto Rico playbook

**Niches to start with** (high ticket, Google-search driven): dentistas, quiroprácticos, clínicas/médicos, abogados, contadores (CPA), talleres de mecánica, contratistas/placas solares, salones/barberías, restaurantes, real estate / alquileres a corto plazo (Rincón, Vieques, Culebra, Isabela).

**Offer.** Keep it simple, with one or two packages, for example a website in 7 days plus a monthly plan for hosting, updates, and Google Business Profile. The monthly plan is what builds steady income, not one-off sales.

**Send safely:**
- **Do not send cold email from @bengalmediapr.com.** Buy a look-alike domain (e.g. `bengalmedia-pr.com`) and set up SPF, DKIM, and DMARC. Warm it up for 2–3 weeks and send at most 30–50 emails per inbox per day. Tools like Instantly or Smartlead handle sending and warm-up. Import `outreach.csv` into them.
- **CAN-SPAM applies in Puerto Rico.** Every email needs your real name, a physical postal address (set `SENDER_ADDRESS`; a PO box works), and an easy way to opt out. The signature added to each draft covers this, so honor opt-outs right away.
- WhatsApp: send messages one at a time by hand from a business number. Bulk-blasting gets the number banned.

**Closing.** Offer a free homepage mockup. Build it with Claude Code in under an hour, deploy it to a Cloudflare Pages preview URL, and send them the link. Seeing their own business on a modern site closes far better than a proposal.

## Roadmap

- [x] Phase 1: leads → audit → personalized outreach (this repo)
- [ ] Phase 2: `sites/` folder with industry templates (bilingual, mobile-first, LocalBusiness schema) and a one-command deploy to Cloudflare Pages
- [ ] Phase 3: bilingual SEO blog on bengalmediapr.com targeting "diseño web en Puerto Rico", "páginas web para negocios en [municipio]", and similar searches
- [ ] Phase 4: Free "Analiza tu web" page on bengalmediapr.com that runs `audit.py` and captures inbound leads
