# Prospectos Metro

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
