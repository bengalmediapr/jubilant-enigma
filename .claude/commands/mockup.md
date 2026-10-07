---
description: Build a free homepage mockup for a lead from the industry templates
argument-hint: "<business name> [industry]"
---

Build a website mockup for this lead: $ARGUMENTS

1. Run `python -m sites.build lead "<business name>"` (add `--industry <key>` if I gave one, or if the
   command can't tell). Industries: dentista, quiropractico, medico, abogado, contador, taller, solar,
   salon, restaurante, alquiler. This writes `sites/clients/<slug>.json` and builds `dist/<slug>/`.
2. Look up the business (its current website, Facebook/Instagram, Google listing) with web search and
   customize `sites/clients/<slug>.json` with what is actually true about them: real services, hours,
   specialties, menu items or prices if published, social links. Any key you add overrides the template;
   see `sites/clients/ejemplo-dentista.json` for the format. Never invent reviews, prices,
   credentials or claims. If you're unsure, keep the template's generic wording.
3. Rebuild with `python -m sites.build client sites/clients/<slug>.json`.
4. Tell me what you customized and the deploy command:
   `npx wrangler pages deploy dist/<slug> --project-name <slug>`
   (the preview URL is what we send the prospect).
