---
description: Find Puerto Rico businesses with web search and add them to data/leads.csv (no Google API key needed)
argument-hint: "<category> <municipio...>  e.g. dentistas Ponce Juana Díaz"
---

Find local businesses for Bengal Media PR to pitch. Arguments: $ARGUMENTS
(first word or quoted phrase = business category in Spanish, the rest = municipios).

For each municipio:
1. Use web search for queries like "<category> en <municipio> Puerto Rico", "<category> <municipio> PR teléfono",
   and directories (Páginas Amarillas PR, Facebook pages, Yelp, Google results). Aim for 15–30 real businesses.
2. For each business you can confirm is real and operating, collect: name, phone, website (if any),
   address, and whether the "website" is only a Facebook/Instagram page.
3. Add each one with:
   `python -m prospector.run add --name "..." --category "<category>" --municipio "<municipio>" --phone "..." --website "..." --address "..."`
   Leave out options you don't know. The command skips duplicates.

Never invent a business, phone number or website. If you are not sure a detail is correct, leave it out.
At the end, run `python -m prospector.run stats` and tell me how many leads have no website,
social-only, or a site to audit. Then suggest running `python -m prospector.run audit`.
