# preparar_github_pages.py
# Copia el dashboard HTML y las figuras a la carpeta docs/
# para que GitHub Pages los sirva correctamente.
#
# Uso:
#   python src/presentacion/preparar_github_pages.py
#
# Resultado:
#   docs/index.html  (copia de dashboard.html)
#   docs/figuras/    (copia de todas las figuras)

import shutil
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.utilidades.config import BASE_DIR, FIGURAS_DIR


DOCS_DIR = BASE_DIR / "docs"
DOCS_FIGURAS = DOCS_DIR / "figuras"

DASHBOARD_HTML = BASE_DIR / "reports" / "dashboard.html"


def main():
    print("=" * 60)
    print("PREPARANDO GITHUB PAGES")
    print("=" * 60)

    # 1. Crear docs/ si no existe
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_FIGURAS.mkdir(parents=True, exist_ok=True)

    # 2. Copiar dashboard.html como docs/index.html
    if not DASHBOARD_HTML.exists():
        print(f"ERROR: no existe {DASHBOARD_HTML}")
        print("Ejecuta primero: python src/presentacion/generar_galeria_html.py")
        return

    destino_html = DOCS_DIR / "index.html"
    shutil.copy2(DASHBOARD_HTML, destino_html)
    print(f"Copiado: {DASHBOARD_HTML.name} -> {destino_html}")

    # 3. Copiar todas las figuras
    if not FIGURAS_DIR.exists():
        print(f"ERROR: no existe {FIGURAS_DIR}")
        return

    figuras = list(FIGURAS_DIR.glob("*.png"))
    print(f"\nCopiando {len(figuras)} figuras...")

    for fig in figuras:
        destino = DOCS_FIGURAS / fig.name
        shutil.copy2(fig, destino)

    print(f"Figuras copiadas a: {DOCS_FIGURAS}")

    # 4. Verificar
    print("\n" + "=" * 60)
    print("VERIFICACION")
    print("=" * 60)
    print(f"docs/index.html: {'OK' if destino_html.exists() else 'FALTA'}")
    print(f"docs/figuras/   : {len(list(DOCS_FIGURAS.glob('*.png')))} figuras")

    print("\nAhora en GitHub:")
    print("  1. Settings -> Pages")
    print("  2. Source: Deploy from a branch")
    print("  3. Branch: main · Folder: /docs")
    print("  4. Save")
    print("\nURL final: https://jdthgp27.github.io/reto5-precios-vivienda-cataluna/")


if __name__ == "__main__":
    main()