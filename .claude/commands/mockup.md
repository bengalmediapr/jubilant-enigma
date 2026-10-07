---
description: Build a personalized website preview for a lead from the industry templates
argument-hint: "<business name> [industry]"
---

Build a website preview for this lead: $ARGUMENTS

Industries: barberia, unas, foodtruck, salon, restaurante, taller, dentista, quiropractico, medico,
abogado, contador, solar, alquiler. The first three (and `salon` with `"theme": {"hero": "poster"}`)
use the bold poster design; prefer them for Instagram-first businesses.

1. Look up the business with web search (Instagram, Facebook, Booksy, Fresha, Uber Eats, Google).
   Confirm it has no website of its own. Collect only what is published: name, address, phone,
   WhatsApp, email, Instagram, hours, services and prices, rating and where it comes from.
2. Write `sites/clients/<slug>.json`, copying the shape of an existing preview such as
   `sites/clients/la-chulada-foodtruck.json`: `"preview": true`, `industry`, `name`, `display_name`
   (short name for the big headline), contact fields, `hours` only if published, `rating` +
   `rating_source` only if published, `content` overrides for real services and prices, and a `lead`
   block (channel, email, why, sources).
3. If `sites/clients/<slug>/` has a logo or photos, add `"assets_dir": "sites/clients/<slug>"`,
   `"logo": "images/<logo file>"` and `"photos": ["images/<file>", ...]` (up to 3 show in the hero).
4. Never invent reviews, prices, hours or claims. Unknown prices stay as the template's examples
   (the preview banner says so) or "Consultar".
5. Run `python -m sites.build previews`, then tell me what you used and the deploy command:
   `npx wrangler pages deploy dist/previews --project-name bengal-previews`.
   Also write a short personalized WhatsApp message (Puerto Rican Spanish, under 70 words) that
   names one real detail about the business and includes `https://bengal-previews.pages.dev/<slug>/`.
