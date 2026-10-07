---
description: Build a business's brand kit (logo, photos, videos, colors, fonts) from files saved off its Instagram/Facebook
argument-hint: "<client slug>"
---

Build the brand kit for client: $ARGUMENTS

1. Make sure `sites/clients/<slug>.json` exists (if not, run /mockup first) and that
   `sites/clients/<slug>/raw/` has the logo (named `logo.*`), photos and any videos. If the user attached
   images in this conversation, copy them there (the logo as `logo.<ext>`).
2. Run `python -m sites.brandkit <slug>`. It optimizes the files, extracts the colors, writes
   `brand.json`, `brand-board.html` and fills logo, photos, gallery and theme colors into the client file.
3. Look at the logo yourself and identify the lettering style. Pick the closest Google Fonts for the
   headline (`theme.font_head`, with `head_weights`, `head_weight` and `char_width` ~0.45 for condensed or
   italic serif, ~0.6 regular, ~0.85 very wide) and a readable body font (`theme.font_body`). Write them in the
   client file. If the extracted colors look off next to the logo (e.g. a background color won), fix
   `theme.primary` / `theme.accent` by hand and add those keys to `"theme_locked"` so a re-run keeps them.
4. Choose the best photo for the hero (the first entry of `photos`): the shop, their best work or their
   signature dish, sharp and well lit. Reorder `photos` and `gallery_images` accordingly.
5. Never touch `sites/industries/` or `sites/templates/`. Everything personal lives in the client file and folder.
6. Rebuild with `python -m sites.build previews`, screenshot the preview if you can, and tell me what you chose.
