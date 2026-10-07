# Guía rápida: de Instagram a cliente

Meta: **10 previews enviados por semana**, en San Juan, Guaynabo y Bayamón (donde puede ir en persona).

## El negocio ideal
- No tiene página web propia (solo Instagram, Facebook, Booksy, Fresha o Uber Eats).
- Instagram activo, con fotos buenas y reseñas buenas.
- WhatsApp o teléfono visible. Email es un bono.
- Industrias que mejor funcionan: barberías, uñas, salones, food trucks, reposterías y talleres.

## Los 5 pasos (por negocio, unos 30 minutos)

**1. Buscar.** En Claude Code: `/find-leads barberías Guaynabo`. Claude busca y apunta los negocios en `data/leads.csv`.

**2. Juntar material.** Del Instagram del negocio, guarde el logo y de 3 a 6 fotos buenas en `sites/clients/<nombre>/`. Anote el horario y los precios si los publican.

**3. Hacer el preview.** En Claude Code: `/mockup "Nombre del negocio"`. Claude arma la página con su nombre, fotos, servicios y contacto. Revísela y publique todos los previews juntos:

```bash
python -m sites.build previews
npx wrangler pages deploy dist/previews --project-name bengal-previews
```
Cada uno queda en `https://bengal-previews.pages.dev/<nombre>/`.

**4. Enviar.** Mande un WhatsApp desde el número del negocio, a mano y uno por uno, con el link del preview. Si tienen email, envíe el mismo mensaje por email.

**5. Dar seguimiento.** Si no contestan, escriba otra vez a los 2 o 3 días. Si sigue sin respuesta, pase en persona con el preview abierto en el celular. Verse en su propia página es lo que más convence.

## Al cerrar
- Decida su precio antes de enviar el primer mensaje (por ejemplo, la página más un plan mensual de hosting y cambios).
- Pida su logo y fotos originales, y confirme los precios y el horario.
- Compre el dominio, quite el aviso de "vista previa" (`"preview_banner": false`) y publique.

## Reglas
- Nunca invente reseñas, precios ni datos. Lo que no esté confirmado se queda como "Consultar".
- Mande los WhatsApp uno por uno. Enviar en masa hace que bloqueen el número.
- Todo email de venta debe incluir su nombre, una dirección postal y una forma de darse de baja (ley CAN-SPAM).
