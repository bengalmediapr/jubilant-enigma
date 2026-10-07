---
description: Write personalized outreach drafts for the next leads in the queue (no API key needed)
argument-hint: "[how many, default 10] [es|en]"
---

Write cold outreach drafts for Bengal Media PR. Arguments: $ARGUMENTS
(first number = how many leads, default 10; `en` = write in English, otherwise Spanish).

1. Run `python -m prospector.run queue --limit <N>` to build `data/outreach_queue.json`
   (leads not drafted yet, best first, with their audit results).
2. Read `prospector/OUTREACH_RULES.md` and follow it exactly.
3. For each lead in the queue, write `data/drafts/<place_id>.json` in the format the rules describe.
   Use only facts from that lead's entry. If a lead has nothing real to pitch, skip it and say why.
4. Run `python -m prospector.run export` to merge the drafts into `data/outreach.csv`
   (it adds the legally required signature and opt-out line).
5. Show me a short table: business, channel (email / WhatsApp), subject. Then show 2 full drafts
   so I can check the tone. Do not send anything.
