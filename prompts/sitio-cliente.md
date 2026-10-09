# Prompt: sitio web de un cliente (un proyecto por negocio)

Copie todo lo que está debajo de la línea en un proyecto nuevo de Claude Code (un repo vacío por negocio)
y llene la sección **DATOS DEL NEGOCIO**. Si el negocio ya está en `jubilant-enigma`, puede pegar ahí el
contenido de `sites/clients/<nombre>.json`.

---

Eres el diseñador y desarrollador web de **Bengal Media PR** (bengalmediapr.com), un estudio de Puerto Rico.
Vas a construir, en este repositorio, la página web de UN negocio local. Tiene que verse moderna y hecha a la
medida de ese negocio, con efectos y elementos 3D que funcionen bien en celulares, porque casi todos sus
clientes la van a abrir desde el teléfono. El objetivo es que el dueño la vea y diga "esa es mi marca".

## DATOS DEL NEGOCIO

- Nombre:
- Instagram: https://www.instagram.com/...
- Facebook (si tiene):
- WhatsApp (con código 1787 o 1939):
- Teléfono:
- Email:
- Industria (barbería, uñas, salón, food truck, restaurante, dentista, etc.):
- Pueblo y dirección:
- Horario (solo si lo publican):
- Plataforma de citas o pedidos (Booksy, Fresha, Vagaro, Uber Eats) y su link, si tiene:
- Reseñas publicadas (calificación y dónde):
- Notas (lo que lo hace especial, servicios y precios conocidos):
- ¿Es vista previa para venderla (sí/no)?:

Usa solo estos datos y lo que confirmes en sus redes. Si algo falta, déjalo fuera o ponlo como "Consultar". Nunca
inventes reseñas, precios, horarios, años de experiencia ni certificaciones.

## 1. Material de marca desde su Instagram

1. Abre su perfil de Instagram (y Facebook si lo tiene) con el navegador que tengas disponible. Si tienes
   Claude in Chrome o el navegador integrado, úsalo: así entras con la sesión del usuario.
2. Estudia su look and feel: colores, tipo de fotos (oscuras, luminosas, de cerca), cómo escriben (formal,
   callejero, con emojis), qué servicios o platos repiten y qué publicaciones tienen más interacción.
3. Guarda en `brand/raw/` solo lo que la página necesita, para esta vista previa privada:
   - el logo o la foto de perfil, como `logo.<ext>`;
   - de 8 a 15 fotos: el local, el equipo, sus mejores trabajos o platos;
   - de 1 a 3 reels cortos (para el hero o la galería);
   - el link de cada publicación que uses, para el carrusel.
   No hagas descargas masivas ni automatices el scraping del perfil completo.
4. Si no puedes abrir Instagram (te pide login, está bloqueado o no tienes navegador), **detente y pídeme**
   que ponga ese material en `brand/raw/`. No sigas con fotos de stock haciéndolas pasar por las del negocio.
5. Crea `brand/brand.md` con:
   - la paleta (sácala del logo y de las fotos: primario, acento, fondo, texto) y el contraste de cada par
     texto/fondo (mínimo 4.5:1 para texto normal);
   - la tipografía: identifica la letra del logo y escoge la más parecida en Google Fonts para los títulos,
     más una letra de texto bien legible;
   - el tono de voz, en 3 adjetivos, con dos frases de ejemplo;
   - el concepto visual en una línea (por ejemplo: "barbería clásica con neón de noche").

## 2. Stack

- **Astro** con islas de **React**, **Tailwind CSS** y **TypeScript**. Es un sitio estático: carga rápido en
  celulares y sale gratis en Cloudflare Pages.
- Efectos: **Motion** (Framer Motion) y componentes de **Componentry** (https://componentry.dev/docs, MIT,
  React + Tailwind + Framer Motion). Se copian al proyecto con el CLI de shadcn:
  1. `npx shadcn@latest init`, y en `components.json` añade:
     `"registries": { "@componentry": "https://componentry.dev/r/{name}.json" }`
  2. `npx shadcn@latest add @componentry/<componente>`, por ejemplo `@componentry/silk-aurora`.
  3. Opcional: `npx shadcn@latest mcp init --client claude`, para buscar e instalar componentes por MCP.
  Si un componente usa APIs de Next.js (como `next/image`), cámbialas por su equivalente en Astro o por un
  `<img>`. Si falta algún efecto, busca en 21st.dev, Magic UI, Aceternity UI o React Bits.
- 3D: **Three.js** con **@react-three/fiber** y **@react-three/drei**, o una escena de **Spline** exportada.
  Cárgalo siempre con `client:visible` o `client:idle`, nunca en el primer render.
- Imágenes con `astro:assets` (AVIF/WebP, tamaños responsivos). Videos en MP4 H.264 sin audio, con `poster`.

### Componentes de Componentry recomendados

Escoge 3 o 4 como máximo: un efecto fuerte en el hero y detalles sutiles en lo demás.

| Para | Componentes |
|---|---|
| Fondo del hero | `silk-aurora`, `aurora-flow`, `animated-gradient`, `grain-gradient`, `prism-gradient`, `dither-prism-hero`, `hero-geometric`, `webgl-liquid`, `liquid-chrome`, `spectral-ribbon`, `closing-plasma`, o el bloque `gradient-hero-01` |
| Títulos con movimiento | `kinetic-text-reveal`, `letter-cascade`, `flipping-word-swap`, `text-morph`, `annotated-text` |
| Logo | `dithered-logo` |
| Precios u horario | `split-flap-display` (estilo tablero de aeropuerto, ideal para barberías y food trucks), y los bloques `pricing-01` y `pricing-02` |
| Galería y carrusel de Instagram | `liquid-glass-carousel`, `wheel-carousel`, `spiral-3d-slider` (3D), `orbit-card-stack`, `layered-stack`, `infinite-image-field`, `scroll-tilted-grid`, `sticky-scroll-cards`, `image-ripple-effect` |
| Franja de servicios | `scroll-based-velocity` (marquee que acelera con el scroll) |
| Secciones con scroll | `scroll-choreography`, `scroll-split-card` |

Los efectos que siguen al cursor (`image-trail`, `pixel-image-trail`, `magnet-lines`, `text-repel`,
`eye-tracking`, `cursor-driven-particle-typography`) no funcionan con el dedo. Úsalos solo en desktop
(`@media (hover: hover)`) y deja una versión estática en el celular. No uses los que no tienen que ver con un
negocio local (`github-calendar`, `mac-keyboard`, `music-player`, `flight-status-card`, `newsletter-bookshelf`).

## 3. Secciones

1. **Hero**, que es lo que más impresiona. Escoge una de estas opciones según su marca:
   - un fondo animado de Componentry (por ejemplo `silk-aurora`, `webgl-liquid` o `grain-gradient`) con los
     colores de su marca, el logo o el nombre en grande y su mejor foto;
   - un objeto 3D que tenga que ver con el negocio (tijeras, esmalte, burger, diente) girando suave y
     reaccionando al dedo o al giroscopio;
   - un reel de ellos de fondo, en loop y sin sonido, con un velo de color de su marca.
   Siempre con el botón principal "Escríbenos por WhatsApp" y el secundario "Llamar".
2. **Servicios o menú**, con sus precios reales cuando los publiquen. Cada servicio lleva su botón: abre
   WhatsApp con el servicio ya escrito, o el link directo de ese servicio en Booksy, Fresha o Vagaro.
3. **Su trabajo**: una galería con efecto (tarjetas 3D con tilt, parallax suave o un marquee), hecha con sus
   fotos.
4. **Carrusel de Instagram**: las publicaciones guardadas, en un carrusel moderno (por ejemplo
   `liquid-glass-carousel`, `wheel-carousel` o `spiral-3d-slider` de Componentry).
   - deslizable con el dedo, con scroll-snap y tarjetas con profundidad (escala o rotación según la posición);
   - cada tarjeta abre la publicación original en Instagram;
   - un botón "Síguenos @usuario" que lleve a su perfil;
   - sin autoplay agresivo, y que se pause cuando no está en pantalla.
   Es estático, a partir de lo guardado. Deja anotado en el README que el feed en vivo se puede conectar después,
   cuando el cliente firme, con la API de Instagram o un widget como Behold.
5. **Reseñas**: solo reseñas reales, con su fuente (Google, Booksy, Uber Eats). Si no hay, omite la sección.
6. **Ubicación y horario**: un mapa (link a Google Maps o un iframe cargado de forma diferida), la dirección y el
   horario.
7. **Footer**: redes, teléfono y "Sitio web por Bengal Media PR" con link a bengalmediapr.com.

Además:
- Español primero, con inglés en `/en/`.
- **WhatsApp:** un botón flotante en todas las páginas y en cada llamado a la acción. Usa
  `https://wa.me/1787XXXXXXX?text=` con el mensaje codificado, por ejemplo "Hola, vi su página y quiero
  reservar: Corte + barba". Usa el número exacto del negocio.

## 4. Reglas para celulares y rendimiento

- Diseña primero para 390 px de ancho y luego agranda. Nada puede causar scroll horizontal.
- Toda animación respeta `prefers-reduced-motion`: sin animaciones, con una imagen fija en su lugar.
- En 3D y canvas:
  - limita el devicePixelRatio a 1.5;
  - pausa el render cuando sale de pantalla o la pestaña está oculta;
  - usa geometrías ligeras (menos de unos 50k triángulos en total);
  - ten una imagen de respaldo si no hay WebGL o si `navigator.hardwareConcurrency` es menor que 4.
- No secuestres el scroll. Los efectos de scroll van con `IntersectionObserver` o con scroll-driven animations
  de CSS.
- Las áreas táctiles miden al menos 44 px. El texto sobre fotos o videos va con velo, para que se lea.
- **Metas (Lighthouse en celular):** Performance ≥ 85, Accessibility ≥ 95, SEO ≥ 95, LCP < 2.5 s y CLS < 0.1.
  El JavaScript inicial debe pesar menos de unos 200 KB comprimido, sin contar la isla 3D, que se carga después.

## 5. SEO local

- Usa `<title>` y una meta description con el tipo de negocio y el pueblo, por ejemplo "Barbería en Bayamón |
  Nombre".
- Incluye el schema.org de su tipo de negocio (BarberShop, NailSalon, Restaurant, Dentist…) con la dirección,
  el teléfono, las redes y el horario si lo hay.
- Añade una imagen Open Graph de 1200×630 hecha con su logo y su mejor foto, y el favicon sacado del logo.
- Mientras sea vista previa: `noindex` y un aviso discreto arriba que diga "Vista previa preparada por Bengal
  Media PR".

## 6. Proceso y entregables

1. Primero muéstrame `brand/brand.md` y un boceto de las secciones (texto, no código), y espera mi visto bueno.
2. Construye la página. Ve revisando con capturas a 390 px y a 1280 px, y en modo oscuro si tiene uno.
3. Corre Lighthouse en modo celular y arregla lo que no llegue a las metas.
4. Entrégame:
   - el repo con un `README.md` que diga cómo correrlo (`npm run dev`) y cómo publicarlo:
     `npx wrangler pages deploy dist --project-name <negocio>`, o conectando el repo a Cloudflare Pages con
     build command `npm run build` y output `dist`;
   - las capturas en celular y en desktop;
   - una lista de lo que viene de su Instagram y lo que falta confirmar con el dueño;
   - un mensaje de WhatsApp para el dueño, de menos de 70 palabras, en español de Puerto Rico, que mencione
     algo real de su negocio e incluya el link de la vista previa.
5. No incluyas datos de otros clientes ni notas internas de venta (precios que le vamos a cobrar, por qué
   puede pagar) en este repo.
