"""Turn a business's own logo, photos and videos into a brand kit for its site.

Put what you saved from their Instagram/Facebook in sites/clients/<slug>/raw/:
  logo.png (or .jpg/.webp)   the logo or profile picture; name it "logo"
  any other images           posts, the shop, their work, their food
  .mp4 / .mov                reels or short videos (compressed if ffmpeg is installed)

  python -m sites.brandkit retoque-guaynabo

It writes, only inside that client's folder and file (templates are never touched):
  sites/clients/<slug>/images/       web-ready photos (WebP), logo and videos
  sites/clients/<slug>/brand.json    extracted colors and the files it produced
  sites/clients/<slug>/brand-board.html   a one-page board to review the kit
  sites/clients/<slug>.json          logo, photos, gallery and theme colors filled in

Fonts can't be read from a picture reliably: open brand-board.html (or ask Claude in
/brandkit) to match the logo's lettering to a Google Font and set theme.font_head.
"""

import argparse
import colorsys
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageOps

from sites.build import ROOT

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm"}


def hex_of(rgb) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def luminance(rgb) -> float:
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def palette(paths: list[Path], colors: int = 8) -> list[tuple[tuple[int, int, int], float]]:
    """Dominant colors across the given images, as (rgb, share), most common first."""
    counts: dict[tuple, int] = {}
    for path in paths:
        img = Image.open(path).convert("RGBA")
        img.thumbnail((200, 200))
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(bg, img).convert("RGB")
        quant = img.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
        pal = quant.getpalette()
        for count, idx in quant.getcolors():
            rgb = tuple(pal[idx * 3: idx * 3 + 3])
            counts[rgb] = counts.get(rgb, 0) + count
    total = sum(counts.values()) or 1
    return sorted(((rgb, n / total) for rgb, n in counts.items()), key=lambda x: -x[1])


def is_neutral(rgb) -> bool:
    h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    return s < 0.18 or l > 0.93 or l < 0.07


def darken_for_text(rgb, bg=(255, 255, 255), target=4.5):
    """Darken a color until white text on it (or it on white) reaches the target contrast."""
    h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    while l > 0.05:
        cand = tuple(round(c * 255) for c in colorsys.hls_to_rgb(h, l, s))
        if contrast(cand, bg) >= target:
            return cand
        l -= 0.02
    return tuple(round(c * 255) for c in colorsys.hls_to_rgb(h, 0.2, s))


def tint(rgb, lightness: float):
    h, _, s = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    return tuple(round(c * 255) for c in colorsys.hls_to_rgb(h, lightness, min(s, 0.45)))


def hue_distance(a, b) -> float:
    ha = colorsys.rgb_to_hls(*(c / 255 for c in a))[0]
    hb = colorsys.rgb_to_hls(*(c / 255 for c in b))[0]
    d = abs(ha - hb)
    return min(d, 1 - d)


def theme_from(logo_colors, photo_colors) -> dict:
    """Primary from the logo's strongest color, accent from a different hue."""
    vivid = [rgb for rgb, share in logo_colors if not is_neutral(rgb) and share > 0.02]
    vivid += [rgb for rgb, share in photo_colors if not is_neutral(rgb) and share > 0.04]
    if not vivid:  # black-and-white logo: keep it monochrome with one warm accent
        primary, accent = (24, 24, 27), (214, 168, 92)
    else:
        primary = vivid[0]
        accent = next((c for c in vivid[1:] if hue_distance(c, primary) > 0.08), tint(primary, 0.72))
    primary_text = darken_for_text(primary)
    accent_ink = (20, 20, 20) if contrast(accent, (20, 20, 20)) >= 4.5 else (255, 255, 255)
    return {
        "primary": hex_of(primary_text),
        "primary_ink": "#ffffff",
        "accent": hex_of(accent),
        "accent_ink": hex_of(accent_ink),
        "bg": hex_of(tint(primary, 0.97)),
        "surface": "#ffffff",
        "ink": hex_of(tint(primary, 0.1)),
        "muted": hex_of(tint(primary, 0.38)),
    }


def save_web_image(src: Path, dest: Path, max_side: int) -> Path:
    img = ImageOps.exif_transpose(Image.open(src))
    img.thumbnail((max_side, max_side))
    dest = dest.with_suffix(".webp")
    img.save(dest, "WEBP", quality=82, method=6)
    return dest


def save_video(src: Path, dest_dir: Path) -> Path:
    dest = dest_dir / (src.stem + ".mp4")
    if shutil.which("ffmpeg"):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", "scale='min(1280,iw)':-2",
                        "-c:v", "libx264", "-crf", "28", "-preset", "slow", "-an", "-movflags", "+faststart",
                        str(dest)], check=True)
        poster = dest.with_suffix(".jpg")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1", "-i", str(dest), "-frames:v", "1",
                        str(poster)], check=False)
    else:
        shutil.copy(src, dest)
    return dest


def board(slug: str, client: dict, kit: dict, folder: Path) -> None:
    sw = "".join(f'<div class="sw" style="background:{v}"><span>{k}<br>{v}</span></div>'
                 for k, v in kit["theme"].items() if k in ("primary", "accent", "bg", "ink", "muted"))
    raw = "".join(f'<div class="sw" style="background:{c}"><span>{c}<br>{round(p * 100)}%</span></div>'
                  for c, p in kit["logo_palette"][:6])
    pics = "".join(f'<img src="images/{Path(p).name}" alt="">' for p in kit["photos"])
    vids = "".join(f'<video src="images/{Path(v).name}" controls muted playsinline></video>' for v in kit["videos"])
    logo = f'<img class="logo" src="images/{Path(kit["logo"]).name}" alt="Logo">' if kit["logo"] else "<p>Sin logo</p>"
    (folder / "brand-board.html").write_text(f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Brand kit · {client['name']}</title>
<style>body{{font-family:system-ui,sans-serif;margin:0;padding:24px 16px;background:#f5f5f4;color:#1c1917}}
main{{max-width:960px;margin:auto;display:grid;gap:24px}}h1{{margin:0}}h2{{font-size:1rem;margin:0 0 8px}}
.row{{display:flex;flex-wrap:wrap;gap:10px}}.sw{{width:120px;height:90px;border-radius:10px;display:flex;align-items:flex-end;
box-shadow:0 0 0 1px #0002}}.sw span{{background:#fffd;font:12px/1.3 ui-monospace,monospace;padding:4px 6px;border-radius:0 6px 0 10px}}
.logo{{max-width:220px;max-height:220px;background:#fff;padding:12px;border-radius:12px}}
.pics{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px}}.pics img,.pics video{{width:100%;aspect-ratio:1;object-fit:cover;border-radius:8px}}
</style></head><body><main><h1>{client['name']}</h1>
<section><h2>Logo</h2>{logo}</section>
<section><h2>Colores del logo</h2><div class="row">{raw}</div></section>
<section><h2>Tema propuesto para la página</h2><div class="row">{sw}</div></section>
<section><h2>Fotos</h2><div class="pics">{pics}</div></section>
{f'<section><h2>Videos</h2><div class="pics">{vids}</div></section>' if vids else ''}
<section><h2>Letra</h2><p>{kit['font_note']}</p></section>
</main></body></html>""", encoding="utf-8")


def run(slug: str) -> dict:
    client_path = ROOT / "clients" / f"{slug}.json"
    if not client_path.exists():
        raise SystemExit(f"Create sites/clients/{slug}.json first (the /mockup command does it).")
    folder = ROOT / "clients" / slug
    raw = folder / "raw"
    if not raw.exists() or not any(raw.iterdir()):
        raw.mkdir(parents=True, exist_ok=True)
        raise SystemExit(f"Put the logo (named logo.*) and photos/videos in {raw}/ and run again.")
    out = folder / "images"
    out.mkdir(exist_ok=True)

    files = sorted(p for p in raw.iterdir() if p.is_file())
    logos = [p for p in files if p.stem.lower().startswith("logo") and p.suffix.lower() in IMAGE_EXT]
    images = [p for p in files if p.suffix.lower() in IMAGE_EXT and p not in logos]
    videos = [p for p in files if p.suffix.lower() in VIDEO_EXT]

    logo = None
    if logos:
        logo = out / ("logo" + (".png" if logos[0].suffix.lower() == ".png" else ".webp"))
        img = ImageOps.exif_transpose(Image.open(logos[0]))
        img.thumbnail((600, 600))
        img.save(logo) if logo.suffix == ".png" else img.save(logo, "WEBP", quality=90)
    # Largest images first: they make the best hero photos.
    images.sort(key=lambda p: -(Image.open(p).size[0] * Image.open(p).size[1]))
    photos = [save_web_image(p, out / f"foto-{i + 1:02d}", 1600) for i, p in enumerate(images)]
    vids = [save_video(p, out) for p in videos]

    logo_pal = palette([logos[0]]) if logos else []
    photo_pal = palette(images[:6]) if images else []
    theme = theme_from(logo_pal, photo_pal)
    kit = {
        "logo": str(logo.relative_to(folder)) if logo else "",
        "photos": [str(p.relative_to(folder)) for p in photos],
        "videos": [str(v.relative_to(folder)) for v in vids],
        "logo_palette": [(hex_of(c), round(s, 3)) for c, s in logo_pal[:8]],
        "photo_palette": [(hex_of(c), round(s, 3)) for c, s in photo_pal[:8]],
        "theme": theme,
        "font_note": "Compare the logo's lettering with Google Fonts and set theme.font_head in the client file "
                     "(ask Claude in /brandkit to identify it).",
    }
    (folder / "brand.json").write_text(json.dumps(kit, ensure_ascii=False, indent=2), encoding="utf-8")

    client = json.loads(client_path.read_text(encoding="utf-8"))
    client["assets_dir"] = f"sites/clients/{slug}/images"
    if kit["logo"]:
        client["logo"] = "images/" + Path(kit["logo"]).name
    if photos:
        client["photos"] = ["images/" + p.name for p in photos[:3]]
        client["hero_image"] = "images/" + photos[0].name
        client["gallery_images"] = ["images/" + p.name for p in photos[:9]]
    client.setdefault("theme", {}).update({k: v for k, v in theme.items()
                                           if k not in client.get("theme_locked", [])})
    client_path.write_text(json.dumps(client, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    board(slug, client, kit, folder)
    return kit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("slug")
    args = parser.parse_args()
    kit = run(args.slug)
    print(f"Logo: {kit['logo'] or 'no'} · {len(kit['photos'])} fotos · {len(kit['videos'])} videos")
    print("Tema:", ", ".join(f"{k} {v}" for k, v in kit["theme"].items() if k in ("primary", "accent", "bg")))
    print(f"Revise sites/clients/{args.slug}/brand-board.html y reconstruya con: python -m sites.build previews")


if __name__ == "__main__":
    main()
