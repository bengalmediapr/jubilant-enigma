"""Export one client's site into its own standalone git repo.

The exported repo holds only that client's built site, nothing from the templates or other
clients, plus deploy configs for Cloudflare Pages, GitHub Pages and GitLab Pages.

  python -m sites.export la-chulada-foodtruck                  # -> exports/la-chulada-foodtruck/
  python -m sites.export la-chulada-foodtruck --out ~/clientes

Then push it to a new, empty repository:
  cd exports/la-chulada-foodtruck
  git remote add origin <url of the new GitHub/GitLab repo>
  git push -u origin main
"""

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from sites.build import ROOT, build_site, site_for

GITHUB_WORKFLOW = """name: Deploy to GitHub Pages
on:
  push:
    branches: [main]
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: public
      - id: deployment
        uses: actions/deploy-pages@v4
"""

GITLAB_CI = """pages:
  stage: deploy
  script:
    - echo "Static site, nothing to build"
  artifacts:
    paths:
      - public
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
"""

README = """# {name}

Sitio web de **{name}** ({municipio}), preparado por Bengal Media PR.
{status}

La página ya está construida en `public/`. No necesita instalar nada para publicarla.

## Publicar

**Cloudflare Pages**
```bash
npx wrangler pages deploy public --project-name {slug}
```

**GitHub Pages:** suba este repo a GitHub y active Settings → Pages → Source: GitHub Actions.
El archivo `.github/workflows/pages.yml` lo publica en cada push a `main`.

**GitLab Pages:** suba este repo a GitLab. El archivo `.gitlab-ci.yml` lo publica en cada push a `main`.

## Cambios

Este repo se genera desde el proyecto principal de Bengal Media PR
(`python -m sites.export {slug}`). Haga los cambios allá y vuelva a exportar.
"""


def export(slug: str, out_root: Path) -> Path:
    client_path = ROOT / "clients" / f"{slug}.json"
    if not client_path.exists():
        names = ", ".join(sorted(p.stem for p in (ROOT / "clients").glob("*.json")))
        raise SystemExit(f"No client '{slug}'. Available: {names}")
    client = json.loads(client_path.read_text(encoding="utf-8"))
    client.pop("lead", None)  # internal sales notes never leave the main repo

    site = site_for(client["industry"], client)
    if site.get("preview"):
        site.setdefault("noindex", True)
        site.setdefault("preview_banner", True)

    repo = out_root / slug
    if repo.exists():
        shutil.rmtree(repo)
    build_site(site, repo / "public")
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "pages.yml").write_text(GITHUB_WORKFLOW, encoding="utf-8")
    (repo / ".gitlab-ci.yml").write_text(GITLAB_CI, encoding="utf-8")
    status = ("Esta es una **vista previa** (no aparece en Google y muestra un aviso arriba). "
              "Al cerrar el cliente, ponga `\"preview\": false` en su archivo y vuelva a exportar."
              if site.get("preview") else "")
    (repo / "README.md").write_text(
        README.format(name=site["name"], municipio=site.get("municipio", ""), slug=slug, status=status),
        encoding="utf-8")

    git = ["git", "-C", str(repo)]
    subprocess.run([*git, "init", "-q", "-b", "main"], check=True)
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "-c", "user.name=Bengal Media PR", "-c", "user.email=noreply@bengalmediapr.com",
                    "commit", "-q", "-m", f"Sitio de {site['name']}"], check=True)
    return repo


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("slug", help="Client file name in sites/clients/, without .json")
    parser.add_argument("--out", default="exports", help="Folder where the client repo is created")
    args = parser.parse_args()
    repo = export(args.slug, Path(args.out).expanduser())
    print(f"Repo listo en {repo}/\n  cd {repo}\n  git remote add origin <url del repo nuevo>\n  git push -u origin main")


if __name__ == "__main__":
    main()
