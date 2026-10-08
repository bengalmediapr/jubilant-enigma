"""Build the Prospectos Metro page from prospectos_metro.py.

  python reports/build_report.py                         # -> reports/site/
  python reports/build_report.py --repo ../prospectosmetro   # -> a repo for GitLab: public/ + README

The page is internal (prices, sales notes): it is marked noindex and should sit behind
Cloudflare Access. See reports/site/README.md.
"""
import sys, html, json, collections, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prospectos_metro as m
e = html.escape
SECTORES = [  # sector, key, categories (order = palette order, validated for color blindness)
 ("Belleza", "belleza", ["Barbería", "Uñas", "Salón"]),
 ("Comida", "comida", ["Food truck", "Restaurante / repostería"]),
 ("Salud", "salud", ["Dentista", "Quiropráctico", "Médico"]),
 ("Profesionales", "prof", ["Abogado", "Contador"]),
 ("Hogar y auto", "hogar", ["Taller", "Techos / solar"]),
 ("Alquiler", "alquiler", ["Alquiler vacacional"]),
]
SEC_OF = {c: (name, key) for name, key, cs in SECTORES for c in cs}
cats = [c for _, _, cs in SECTORES for c in cs]
rows = sorted(m.rows(), key=lambda r: cats.index(r["categoria"]))
def handle(url):
    return "@" + url.rstrip("/").split("/")[-1] if "instagram" in url else "Facebook"
def host(u): return re.sub(r"^https?://(www\.)?", "", u).split("/")[0]
import re as _re
for r in rows:
    r["slug_id"] = "n-" + _re.sub(r"[^a-z0-9]+", "-", r["nombre"].lower()).strip("-")

def plat_html(r):
    if r["plataforma_citas"] == "No detectada":
        return '<span class="none">No detectada (WhatsApp o llamada)</span>'
    name = e(r["plataforma_citas"])
    if r["link_plataforma"]:
        name = f'<a href="{e(r["link_plataforma"])}">{name}</a>'
    return f'{name} · <span class="cost">{e(r["costo_actual_plataforma"])}</span>'

cards = []
for i, r in enumerate(rows):
    links = []
    if r["instagram"]: links.append(f'<a href="{e(r["instagram"])}">{e(handle(r["instagram"]))}</a>')
    if r["facebook"]: links.append(f'<a href="{e(r["facebook"])}">Facebook</a>')
    def f(label, val, cls=""):
        v = e(val) if val else '<span class="none">No encontrado</span>'
        return f'<div class="f {cls}"><dt>{label}</dt><dd>{v}</dd></div>'
    src = " · ".join(f'<a href="{e(s)}">{e(host(s))}</a>' for s in r["fuentes"].split())
    cards.append(f'''
<article class="biz" id="{e(r["slug_id"])}" style="--sec: var(--s-{SEC_OF[r["categoria"]][1]})" data-cat="{e(r["categoria"])}" data-pago="{r["potencial_pago"]}" data-conf="{r["confianza"]}" data-plat="{'1' if r['plataforma_citas'] != 'No detectada' else '0'}" data-ola="{r['ola']}">
  <header>
    <p class="secb"><i aria-hidden="true"></i>{e(SEC_OF[r["categoria"]][0])} · {e(r["categoria"])}</p>
    <div class="ttl"><h3>{e(r["nombre"])}</h3><p class="loc">{e(r["pueblo"])} · {e(r["direccion"])}</p></div>
    <div class="tags">{'<span class="tag ola">Ola 1</span>' if r["ola"] else ''}<span class="tag pago-{r["potencial_pago"]}">Pago {r["potencial_pago"].lower()}</span><span class="tag conf-{r["confianza"]}">Verificación {r["confianza"].lower()}</span></div>
  </header>
  <p class="social">{" · ".join(links)}</p>
  <dl>
    {f("Teléfono", r["telefono"], "num")}
    {f("WhatsApp", r["whatsapp"], "num")}
    {f("Email", r["email"])}
    {f("Reseñas", r["resenas"] if r["resenas"] != "No encontradas" else "")}
  </dl>
  <p class="sig"><b>Por qué puede pagar:</b> {e(r["senales_de_pago"])}</p>
  <p class="web"><b>Página web:</b> {e(r["verificacion_web"])}</p>
  <div class="offer">
    <p><b>Citas hoy:</b> {plat_html(r)}</p>
    <p class="pkg"><b>Propuesta: {e(r["paquete"])}</b> <span class="price">${r["setup_usd"]:,} + ${r["mensual_usd"]}/mes</span></p>
  </div>
  {f'<p class="src">Fuentes: {src}</p>' if src else ''}
</article>''')
count = collections.Counter(r["categoria"] for r in rows)
chips = '<button type="button" class="chip on" data-filter="all" id="c-all">Todas <span>{}</span></button>'.format(len(rows)) + "".join(
    f'<button type="button" class="chip" style="--sec: var(--s-{SEC_OF[c][1]})" data-filter="{e(c)}" id="c-{i}"><i aria-hidden="true"></i>{e(c)} <span>{count[c]}</span></button>' for i, c in enumerate(cats))
legend = "".join(f'<li style="--sec: var(--s-{k})"><i aria-hidden="true"></i>{e(n)} <span>{sum(count[c] for c in cs)}</span></li>' for n, k, cs in SECTORES)
desc = "".join(f'<li><b>{e(n)}</b> ({e(p)}): {e(w)}</li>' for n, p, w in m.DESCARTADOS)
n_alto = sum(r["potencial_pago"] == "Alto" for r in rows)
n_alta = sum(r["confianza"] == "Alta" for r in rows)
n_wa = sum(bool(r["whatsapp"]) for r in rows); n_em = sum(bool(r["email"]) for r in rows)
n_plat = sum(r["plataforma_citas"] != "No detectada" for r in rows)
ola = sorted([r for r in rows if r["ola"]], key=lambda r: (r["prioridad"], cats.index(r["categoria"])))
def contacto(r):
    if r["whatsapp"]:
        return f'<span class="wa">WhatsApp</span> <span class="sel">{e(r["whatsapp"])}</span>'
    if r["telefono"]:
        return f'<span class="sel">{e(r["telefono"])}</span> <span class="muted">(probar WhatsApp)</span>'
    return '<span class="muted">Solo Instagram DM</span>'
ola_rows = "".join(
    f'<li style="--sec: var(--s-{SEC_OF[r["categoria"]][1]})"><span class="rk">{i}</span>'
    f'<div class="ol-main"><a class="ol-name" href="#{r["slug_id"]}">{e(r["nombre"])}</a>'
    f'<span class="ol-meta"><i aria-hidden="true"></i>{e(r["categoria"])} · {e(r["pueblo"])} · {e(r["paquete"])} ${r["setup_usd"]:,} + ${r["mensual_usd"]}/mes</span></div>'
    f'<div class="ol-c">{contacto(r)}</div>'
    f'<div class="ol-ig">{f"""<a href="{e(r["instagram"])}">{e(handle(r["instagram"]))}</a>""" if r["instagram"] else ""}</div></li>'
    for i, r in enumerate(ola, 1))
pk_count = collections.Counter(r["paquete_key"] for r in rows)
pk_rows = "".join(
    f'<tr><th scope="row">{e(n)}</th><td>{e(d)}</td><td class="num">${st:,}</td><td class="num">${mo}</td><td class="num">{pk_count[k]}</td></tr>'
    for k, (n, st, mo, d) in m.PAQUETES.items())
page = f'''<title>Prospectos Metro</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Figtree:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap">
<style>
/* Layout: a working prospect ledger. Summary and method first, then filters, then one card per business. */
:root {{
  --bg: #f3f2ee; --surface: #ffffff; --ink: #1b1d22; --muted: #646872; --line: #e1dfd8; --accent: #0f5c4d;
  --hi: #0f5c4d; --hi-bg: #e1f1ec; --mid: #8a5a00; --mid-bg: #fbefd5; --lo: #9b2c2c; --lo-bg: #fbe3e1;
  --s-belleza: #e87ba4; --s-comida: #eda100; --s-salud: #1baf7a; --s-prof: #4a3aa7; --s-hogar: #eb6834; --s-alquiler: #2a78d6;
  --serif: "Fraunces", Georgia, serif; --body: "Figtree", system-ui, sans-serif; --mono: "JetBrains Mono", ui-monospace, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #15161a; --surface: #1e2025; --ink: #eceae5; --muted: #a2a5ad; --line: #30333a; --accent: #5fc9ad;
  --hi: #6fd6b9; --hi-bg: #173a32; --mid: #f0c26a; --mid-bg: #3a2f17; --lo: #f19a94; --lo-bg: #3d1f1d;
  --s-belleza: #d55181; --s-comida: #c98500; --s-salud: #199e70; --s-prof: #9085e9; --s-hogar: #d95926; --s-alquiler: #3987e5; color-scheme: dark; }} }}
:root[data-theme="dark"] {{ --bg: #15161a; --surface: #1e2025; --ink: #eceae5; --muted: #a2a5ad; --line: #30333a; --accent: #5fc9ad;
  --hi: #6fd6b9; --hi-bg: #173a32; --mid: #f0c26a; --mid-bg: #3a2f17; --lo: #f19a94; --lo-bg: #3d1f1d;
  --s-belleza: #d55181; --s-comida: #c98500; --s-salud: #199e70; --s-prof: #9085e9; --s-hogar: #d95926; --s-alquiler: #3987e5; color-scheme: dark; }}
* {{ box-sizing: border-box; }}
body {{ background: var(--bg); color: var(--ink); font: 400 15.5px/1.55 var(--body); padding-inline: 16px; }}
.wrap {{ max-width: 1080px; margin-inline: auto; padding-block: 36px 64px; display: grid; gap: 28px; }}
.wrap > * {{ min-width: 0; }}
.kick {{ font: 500 12px/1 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--accent); margin: 0 0 10px; }}
h1 {{ font: 700 clamp(2rem, 6vw, 3.2rem)/1.02 var(--serif); margin: 0 0 12px; letter-spacing: -.02em; }}
h2 {{ font: 700 1.35rem/1.2 var(--serif); margin: 0 0 10px; }}
.lede {{ margin: 0; color: var(--muted); max-width: 66ch; font-size: 1.05rem; }}
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }}
.stat {{ background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; }}
.stat b {{ display: block; font: 700 1.9rem/1 var(--serif); font-variant-numeric: tabular-nums; }}
.stat span {{ color: var(--muted); font-size: .88rem; }}
.method {{ background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 18px 20px; }}
.method ul {{ margin: 0; padding-left: 18px; display: grid; gap: 6px; color: var(--muted); }}
.method b {{ color: var(--ink); }}
.filters {{ display: grid; gap: 10px; position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: var(--bg); padding-block: 10px; border-bottom: 1px solid var(--line); }}
.chips {{ display: flex; gap: 6px; flex-wrap: wrap; }}
.chip {{ font: 500 .88rem var(--body); border: 1px solid var(--line); background: var(--surface); color: var(--ink); border-radius: 999px; padding: 6px 12px; cursor: pointer; }}
.chip span {{ color: var(--muted); font-variant-numeric: tabular-nums; }}
.chip.on {{ background: var(--ink); color: var(--bg); border-color: var(--ink); }}
.chip.on span {{ color: inherit; opacity: .7; }}
.toggles {{ display: flex; gap: 16px; flex-wrap: wrap; font-size: .9rem; color: var(--muted); align-items: center; }}
.toggles label {{ display: flex; gap: 6px; align-items: center; cursor: pointer; }}
.shown {{ font-variant-numeric: tabular-nums; }}
.list {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 330px), 1fr)); gap: 12px; }}
.biz {{ background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 16px; display: grid; gap: 10px; align-content: start; min-width: 0; }}
.biz header {{ display: grid; gap: 8px; }}
h3 {{ font: 700 1.05rem/1.25 var(--body); margin: 0; }}
.loc {{ margin: 2px 0 0; color: var(--muted); font-size: .86rem; }}
.tags {{ display: flex; gap: 6px; flex-wrap: wrap; }}
.tag {{ font-size: .74rem; font-weight: 600; padding: 3px 8px; border-radius: 6px; }}
.pago-Alto, .conf-Alta {{ background: var(--hi-bg); color: var(--hi); }}
.pago-Medio, .conf-Media {{ background: var(--mid-bg); color: var(--mid); }}
.conf-Baja {{ background: var(--lo-bg); color: var(--lo); }}
.social {{ margin: 0; font-weight: 600; }}
.social a, .src a {{ color: var(--accent); }}
dl {{ margin: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 8px 12px; }}
dt {{ font-size: .72rem; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }}
dd {{ margin: 0; font-size: .9rem; overflow-wrap: anywhere; }}
.num dd {{ font-variant-numeric: tabular-nums; user-select: all; }}
.none {{ color: var(--muted); font-style: italic; }}
.sig, .web {{ margin: 0; font-size: .9rem; }}
.web {{ color: var(--muted); }}
.src {{ margin: 0; font-size: .78rem; color: var(--muted); overflow-wrap: anywhere; }}
.empty {{ color: var(--muted); }}
.tag.ola {{ background: var(--ink); color: var(--bg); }}
.wave code {{ font-size: .8em; }}
.ola {{ list-style: none; margin: 8px 0 0; padding: 0; display: grid; }}
.ola li {{ display: grid; grid-template-columns: 34px minmax(0, 2.2fr) minmax(0, 1.4fr) minmax(0, 1fr); gap: 4px 12px; align-items: center; padding: 10px 0; border-top: 1px solid var(--line); }}
.rk {{ font: 700 1.1rem/1 var(--serif); color: var(--muted); font-variant-numeric: tabular-nums; }}
.ol-main {{ display: grid; gap: 2px; min-width: 0; }}
.ol-name {{ font-weight: 700; color: var(--ink); text-decoration: none; }}
.ol-name:hover {{ text-decoration: underline; }}
.ol-meta {{ display: block; font-size: .82rem; color: var(--muted); }}
.ol-meta i {{ width: 9px; height: 9px; border-radius: 50%; background: var(--sec); display: inline-block; margin-right: 6px; vertical-align: 1px; }}
.ol-c, .ol-ig {{ font-size: .88rem; min-width: 0; overflow-wrap: anywhere; }}
.ol-ig a {{ color: var(--accent); font-weight: 600; }}
.wa {{ font-weight: 700; color: var(--hi); }}
.muted {{ color: var(--muted); }}
@media (max-width: 760px) {{ .ola li {{ grid-template-columns: 30px minmax(0, 1fr); }} .ol-c, .ol-ig {{ grid-column: 2; }} }}
.biz {{ border-top: 5px solid var(--sec); }}
.secb {{ margin: 0; display: flex; align-items: center; gap: 7px; font-size: .74rem; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }}
.secb i, .chip i, .legend i {{ width: 10px; height: 10px; border-radius: 50%; background: var(--sec); flex: none; display: inline-block; }}
.chip {{ display: inline-flex; align-items: center; gap: 6px; }}
.chip.on i {{ box-shadow: 0 0 0 2px var(--bg); }}
.legend {{ list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 6px 16px; font-size: .88rem; font-weight: 600; }}
.legend li {{ display: inline-flex; align-items: center; gap: 6px; }}
.legend span {{ color: var(--muted); font-weight: 500; font-variant-numeric: tabular-nums; }}
.offer {{ background: var(--bg); border-radius: 10px; padding: 10px 12px; display: grid; gap: 4px; font-size: .9rem; }}
.offer p {{ margin: 0; }}
.offer a {{ color: var(--accent); }}
.cost {{ color: var(--muted); }}
.pkg {{ display: flex; justify-content: space-between; gap: 8px; flex-wrap: wrap; }}
.price {{ font-weight: 700; color: var(--accent); font-variant-numeric: tabular-nums; white-space: nowrap; }}
.pricing h3 {{ font: 700 1.05rem/1.3 var(--body); margin: 22px 0 8px; }}
.pricing h4 {{ font: 700 1rem/1.3 var(--body); margin: 0 0 6px; }}
.pricing p {{ color: var(--muted); }}
.pricing p b, .pricing li b {{ color: var(--ink); }}
.note {{ margin: 0 0 12px; }}
.tbl {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; }}
table {{ border-collapse: collapse; width: 100%; min-width: 620px; font-size: .9rem; }}
th, td {{ text-align: left; vertical-align: top; padding: 10px 12px; border-bottom: 1px solid var(--line); }}
thead th {{ font-size: .74rem; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); background: var(--bg); }}
tbody th {{ font-weight: 700; white-space: nowrap; }}
td.num {{ font-variant-numeric: tabular-nums; white-space: nowrap; font-weight: 600; }}
tbody tr:last-child th, tbody tr:last-child td {{ border-bottom: 0; }}
.two {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr)); gap: 12px; }}
.two > div {{ border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px; background: var(--bg); min-width: 0; }}
.two p {{ margin: 0 0 8px; }}
@media (max-width: 700px) {{ .filters {{ position: static; }} }}
.drop ul {{ margin: 0; padding-left: 18px; display: grid; gap: 4px; color: var(--muted); }}
button:focus-visible, a:focus-visible, input:focus-visible {{ outline: 3px solid var(--accent); outline-offset: 2px; }}
</style>

<div class="wrap">
  <header>
    <p class="kick">Bengal Media PR · Octubre 2026</p>
    <h1>Prospectos Metro</h1>
    <p class="lede">{len(rows)} negocios de San Juan, Guaynabo y Bayamón, en {len(cats)} categorías, que tienen Instagram o Facebook y a los que no les encontré página web propia. Empiece por la Ola 1: los {len(ola)} que tienen WhatsApp o Instagram, en orden de prioridad. Cada negocio trae la plataforma de citas que usa hoy, lo que le cuesta y el paquete con el precio que le sugiero cobrarle. Abajo están los precios y cómo presentarlos.</p>
  </header>

  <section class="stats" aria-label="Resumen">
    <div class="stat"><b>{len(rows)}</b><span>negocios</span></div>
    <div class="stat"><b>{n_alto}</b><span>con potencial de pago alto</span></div>
    <div class="stat"><b>{n_alta}</b><span>sin web confirmado con certeza</span></div>
    <div class="stat"><b>{n_wa}</b><span>con WhatsApp confirmado</span></div>
    <div class="stat"><b>{n_em}</b><span>con email</span></div>
    <div class="stat"><b>{len(ola)}</b><span>en la Ola 1 (WhatsApp o Instagram)</span></div>
    <div class="stat"><b>{n_plat}</b><span>ya pagan una plataforma de citas o pedidos</span></div>
  </section>

  <section class="method">
    <h2>Cómo lo verifiqué y qué falta</h2>
    <ul>
      <li><b>Sin web:</b> busqué cada negocio por nombre. <b>Verificación alta</b> quiere decir que solo aparecen en Instagram, Facebook o directorios (Booksy, Fresha, Uber Eats). <b>Media</b> quiere decir que no apareció ninguna web, pero hay poca información. <b>Baja</b> quiere decir que hay que confirmar la dirección y los datos.</li>
      <li><b>Seguidores:</b> no los pude ver. Desde aquí no hay acceso a Instagram, Facebook ni Google Maps; los ve al abrir cada perfil.</li>
      <li><b>Reseñas:</b> solo las pongo donde las encontré publicadas (Uber Eats, Fresha). Casi ninguna reseña de Google se pudo ver.</li>
      <li><b>WhatsApp y email:</b> solo los que el negocio publica. Casi todos usan el teléfono también para WhatsApp, pero eso no está confirmado.</li>
      <li><b>Potencial de pago:</b> es mi juicio a partir de señales: tipo de negocio, años operando, varias sucursales, precios altos o zona de mucho dinero.</li>
    </ul>
  </section>



  <section class="method wave" id="ola-1">
    <h2>Ola 1: por dónde empezar ({len(ola)} negocios)</h2>
    <p class="note">Ninguno tiene página web propia; todos tienen WhatsApp o Instagram, y su dirección y teléfono están confirmados. Están en orden: arriba, los que pueden pagar, de los que estoy seguro de que no tienen web, con WhatsApp confirmado o que ya pagan una plataforma.</p>
    <p class="note"><b>De cada Instagram guarde:</b> el logo o la foto de perfil (con el nombre <code>logo</code>), de 6 a 10 fotos buenas y 1 o 2 reels, en <code>sites/clients/&lt;nombre&gt;/raw/</code>, o mándemelos aquí. Con eso armo cada página con su marca usando <code>/brandkit</code>.</p>
    <ol class="ola">{ola_rows}</ol>
  </section>

  <section class="method pricing" id="precios">
    <h2>Precios y paquetes</h2>
    <p class="note">Su precio de instalación es un solo pago. El mensual cubre hosting, dominio, certificado SSL, cambios pequeños y soporte. Como referencia, en Puerto Rico las páginas se venden entre $450 y $2,295, y el mantenimiento de una agencia pequeña cuesta entre $50 y $200 al mes.</p>
    <div class="tbl"><table>
      <thead><tr><th scope="col">Paquete</th><th scope="col">Qué incluye</th><th scope="col">Instalación</th><th scope="col">Mensual</th><th scope="col">Prospectos</th></tr></thead>
      <tbody>{pk_rows}</tbody>
    </table></div>

    <h3>Lo que ya pagan por sus citas (precios publicados en 2026)</h3>
    <div class="tbl"><table>
      <thead><tr><th scope="col">Plataforma</th><th scope="col">Mensualidad</th><th scope="col">Comisiones</th><th scope="col">Quiénes la usan</th></tr></thead>
      <tbody>
        <tr><th scope="row">Booksy</th><td>$29.99 + $20 por empleado</td><td>Boost: 30% de la primera visita de cada cliente nuevo que llega por la app ($10 a $100)</td><td>Santurce La Barbería, Estudio La Barbería, Jireh, Jean C Stilo</td></tr>
        <tr><th scope="row">Fresha</th><td>$19.95 individual o $14.95 por empleado</td><td>20% (mínimo $6) del primer servicio de cada cliente nuevo del marketplace; tarjetas desde 2.29% + $0.20</td><td>167 Barber Shop, Retoque, JJ, Sport, Crea'tif, Top Nail Bar</td></tr>
        <tr><th scope="row">Vagaro</th><td>$23.99 + $10 por usuario</td><td>Tarjetas 2.75%</td><td>Curl Boss</td></tr>
        <tr><th scope="row">Jane App</th><td>Desde $54</td><td>Cargos extra por SMS y por cada profesional</td><td>Aviva Family Chiropractic</td></tr>
        <tr><th scope="row">Uber Eats</th><td>No tiene mensualidad</td><td>7–10% en pedidos para recoger, 20–30% en delivery</td><td>La Chulada, Guaynabo Bakery</td></tr>
      </tbody>
    </table></div>

    <h3>Las dos maneras de integrar las citas</h3>
    <div class="two">
      <div><h4>1. Citas conectadas ($900 + $69/mes)</h4>
        <p>Siguen con Booksy o Fresha. En la página, cada servicio tiene su botón "Reservar" que abre ese mismo servicio en su plataforma.</p>
        <p><b>Lo que ganan:</b> el cliente que reserva desde su página entra como cliente directo, y Fresha y Booksy no cobran la comisión de cliente nuevo por esas citas. No cambian nada de cómo trabajan.</p>
        <p><b>Ideal para:</b> negocios pequeños o que reciben muchos clientes nuevos por la app.</p></div>
      <div><h4>2. Citas propias ($1,600 + $99/mes)</h4>
        <p>Las reservas se hacen dentro de su página: cada servicio con su precio, su duración y su barbero, con confirmación por WhatsApp o email. Dejan de pagar Booksy o Fresha.</p>
        <p><b>Lo que ganan:</b> no pagan mensualidad por empleado ni comisiones, su marca va primero y los datos de sus clientes son suyos. Por dentro puede usar Setmore (gratis hasta 4 empleados) o un sistema propio en Cloudflare (gratis hasta 100,000 visitas al día), así que casi todo el mensual es ganancia suya.</p>
        <p><b>Lo que pierden:</b> los clientes nuevos que hoy les llegan buscando en la app de Booksy o Fresha. Ofrézcalo a los que ya tienen clientela fija, como Santurce La Barbería (4 barberos y más de 1,100 reseñas) o Top Nail Bar (2,590 votos).</p></div>
    </div>

    <h3>Cómo presentarlo</h3>
    <ul>
      <li><b>Compare con lo que ya pagan.</b> Por ejemplo, Santurce La Barbería paga cerca de $90–$120 al mes por 4 perfiles en Booksy. Con Citas propias paga $99 al mes y además tiene página web.</li>
      <li><b>Food trucks y restaurantes:</b> Uber Eats se queda con 7–10% de cada pedido para recoger. Con Pedidos directos, sus clientes fijos piden por la página y el negocio se queda con esa comisión. Mantengan Uber Eats para el delivery.</li>
      <li><b>Profesionales</b> (dentistas, médicos, abogados, CPA): no están comparando contra una app sino contra no existir en Google. El argumento es conseguir pacientes y clientes nuevos.</li>
      <li><b>Su costo real:</b> el hosting en Cloudflare es gratis y el dominio cuesta unos $10–20 al año. Casi todo el mensual es ganancia; su trabajo es el tiempo de los cambios.</li>
      <li><b>Antes de cobrar,</b> confirme cuántos empleados tienen en la plataforma: el costo actual que puse es un estimado.</li>
    </ul>
  </section>

  <section class="filters" aria-label="Filtros">
    <ul class="legend" aria-label="Sectores">{legend}</ul>
    <div class="chips" role="group" aria-label="Categoría">{chips}</div>
    <div class="toggles">
      <label><input type="checkbox" id="f-alto"> Solo potencial de pago alto</label>
      <label><input type="checkbox" id="f-conf"> Ocultar verificación baja</label>
      <label><input type="checkbox" id="f-ola"> Solo Ola 1</label>
      <label><input type="checkbox" id="f-plat"> Solo los que usan plataforma de citas</label>
      <span class="shown" id="shown"></span>
    </div>
  </section>

  <main class="list" id="list">{"".join(cards)}
  </main>
  <p class="empty" id="empty" hidden>No hay negocios con esos filtros.</p>

  <section class="method drop">
    <h2>Descartados</h2>
    <ul>{desc}</ul>
  </section>
</div>

<script>
(function () {{
  var cat = "all";
  var cards = Array.prototype.slice.call(document.querySelectorAll(".biz"));
  var alto = document.getElementById("f-alto"), conf = document.getElementById("f-conf"), plat = document.getElementById("f-plat"), ola = document.getElementById("f-ola");
  function apply() {{
    var n = 0;
    cards.forEach(function (c) {{
      var ok = (cat === "all" || c.dataset.cat === cat) && (!alto.checked || c.dataset.pago === "Alto") && (!conf.checked || c.dataset.conf !== "Baja") && (!plat.checked || c.dataset.plat === "1") && (!ola.checked || c.dataset.ola === "1");
      c.hidden = !ok; if (ok) n++;
    }});
    document.getElementById("shown").textContent = n + " de " + cards.length + " visibles";
    document.getElementById("empty").hidden = n > 0;
  }}
  document.querySelectorAll(".chip").forEach(function (b) {{
    b.addEventListener("click", function () {{
      cat = b.dataset.filter;
      document.querySelectorAll(".chip").forEach(function (x) {{ x.classList.toggle("on", x === b); }});
      apply();
    }});
  }});
  alto.addEventListener("change", apply); conf.addEventListener("change", apply); plat.addEventListener("change", apply); ola.addEventListener("change", apply);
  apply();
}})();
</script>
'''
README_REPO = """# Prospectos Metro

Reporte interno de Bengal Media PR: negocios de San Juan, Guaynabo y Bayamón sin página web,
con contactos, plataforma de citas, propuesta y precio. **Es información interna**: mantenga este
repo privado y la página protegida con Cloudflare Access (paso 3).

La página ya está construida en `public/`. No hay que instalar nada.

## 1. Conectar Cloudflare Pages a este repo (se publica solo en cada push)

1. Cloudflare → **Workers & Pages** → **Create** → pestaña **Pages** → **Connect to Git** → **GitLab**.
2. Escoja `bengalmediapr/prospectosmetro`.
3. Configuración de build:
   - Framework preset: **None**
   - Build command: *(vacío)*
   - Build output directory: **`public`**
4. **Save and Deploy**. Queda en `https://prospectosmetro.pages.dev` (o el nombre que escoja).

Sin conectar GitLab también se puede subir directo: `npx wrangler pages deploy public --project-name prospectosmetro`

## 2. Actualizar el reporte

Desde el proyecto principal (jubilant-enigma):

```bash
python reports/build_report.py --repo ../prospectosmetro
cd ../prospectosmetro && git push
```

## 3. Protegerlo para que solo usted lo vea

La página no aparece en Google (`noindex`), pero cualquiera con el link podría abrirla.
Cloudflare → **Zero Trust** → **Access** → **Applications** → **Add an application** → **Self-hosted**:
- Dominio: `prospectosmetro.pages.dev`
- Política: **Allow**, *Include* → **Emails** → su email
- Inicio de sesión: código por email (One-time PIN)

Así, para abrir la página hay que poner un código que le llega a su email.
"""

# The artifact host adds the document shell; a standalone deploy needs its own.
title, _, body = page.partition("\n")
doc = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
{title}
{body.split("<style>", 1)[0]}<style>
body {{ margin: 0; }}
{body.split("<style>", 1)[1].replace("</style>", "</style>\n</head>\n<body>", 1)}
</body>
</html>
"""
args = sys.argv[1:]
repo = Path(args[args.index("--repo") + 1]).expanduser() if "--repo" in args else None
out = repo / "public" if repo else (Path(args[0]) if args else HERE / "site")
out.mkdir(parents=True, exist_ok=True)
(out / "index.html").write_text(doc, encoding="utf-8")
(out / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
(out / "_headers").write_text("/*\n  X-Robots-Tag: noindex, nofollow\n  Referrer-Policy: no-referrer\n", encoding="utf-8")
print(f"{len(rows)} negocios -> {out / 'index.html'}")

if repo:
    (repo / "README.md").write_text(README_REPO, encoding="utf-8")
    import subprocess
    if not (repo / ".git").exists():
        subprocess.run(["git", "-C", str(repo), "init", "-q", "-b", "main"], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=Bengal Media PR", "-c", "user.email=noreply@bengalmediapr.com",
                    "commit", "-q", "-m", "Actualizar Prospectos Metro"], check=False)
    print(f"Repo listo en {repo}")
