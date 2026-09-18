# generar_dashboard.py
# Genera un dashboard consolidado con las 12 figuras clave del proyecto.
#
# Uso:
#   python src/presentacion/generar_dashboard.py
#
# Salida:
#   reports/dashboard.png (grid 4x3)
#   reports/dashboard.pdf (version imprimible)

from pathlib import Path
import sys
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.utilidades.config import BASE_DIR, FIGURAS_DIR


SALIDA_PNG = BASE_DIR / "reports" / "dashboard.png"
SALIDA_PDF = BASE_DIR / "reports" / "dashboard.pdf"

# Colores
COLOR_PRIMARIO = "#2E86AB"
COLOR_ACENTO = "#F18F01"
COLOR_TEXTO = "#2C3E50"


# ============================================================
# CONFIGURACION DE LAS 12 FIGURAS
# ============================================================
FIGURAS = [
    # Fila 1: Contexto general
    ("01_serie_temporal_global.png",
     "Evolución mensual de transacciones (2012-2025)"),
    ("03_heatmap_anio_mes.png",
     "Estacionalidad: heatmap año × mes"),
    ("04_ranking_barrios.png",
     "Top 15 / Bottom 15 barrios por transacciones"),

    # Fila 2: Análisis complementario
    ("08_distribucion_target.png",
     "Distribución del target (skewness = 2,76)"),
    ("20_serpavi_vs_transacciones.png",
     "SERPAVI: alquiler vs transacciones por distrito"),
    ("24_compradores_extranjeros.png",
     "% de compradores extranjeros por distrito"),

    # Fila 3: Modelado
    ("09_comparativa_baseline.png",
     "Comparativa de modelos baseline"),
    ("16_shap_bar.png",
     "SHAP: importancia de features"),
    ("12_analisis_residuos.png",
     "Análisis de residuos del modelo"),

    # Fila 4: Interpretación
    ("17_shap_dependence_top3.png",
     "SHAP: dependence plots (top 3)"),
    ("18_shap_waterfall.png",
     "SHAP: waterfall del peor caso"),
    ("26_inquilinos_extranjeros_estimado.png",
     "Estimación de inquilinos extranjeros"),
]


# ============================================================
# DASHBOARD
# ============================================================
def generar_dashboard():
    print("=" * 60)
    print("GENERANDO DASHBOARD CONSOLIDADO")
    print("=" * 60)

    # Figura grande: 4 filas x 3 columnas
    fig = plt.figure(figsize=(22, 28), facecolor="white")

    # GridSpec con espacio para titulo general
    gs = GridSpec(
        5, 3, figure=fig,
        height_ratios=[0.4, 1, 1, 1, 1],
        hspace=0.35, wspace=0.25,
        left=0.04, right=0.96, top=0.97, bottom=0.03,
    )

    # ---------------------------------------------------------
    # Titulo general (fila 0, abarcando 3 columnas)
    # ---------------------------------------------------------
    ax_titulo = fig.add_subplot(gs[0, :])
    ax_titulo.axis("off")

    ax_titulo.text(
        0.5, 0.75,
        "Predicción de Transacciones Inmobiliarias en Barcelona",
        ha="center", va="center", fontsize=26, fontweight="bold",
        color=COLOR_PRIMARIO, transform=ax_titulo.transAxes,
    )
    ax_titulo.text(
        0.5, 0.35,
        "Reto 5 · Business Intelligence y Big Data · Curso Odisea Data 2025",
        ha="center", va="center", fontsize=14, style="italic",
        color=COLOR_TEXTO, transform=ax_titulo.transAxes,
    )
    ax_titulo.text(
        0.5, 0.05,
        "Modelo XGBoost (objetivo Poisson) · R² = 0,617 · RMSE = 15,77 · "
        "68 barrios × 167 meses · 254.732 transacciones analizadas",
        ha="center", va="center", fontsize=12,
        color=COLOR_ACENTO, fontweight="bold",
        transform=ax_titulo.transAxes,
    )

    # ---------------------------------------------------------
    # 12 figuras en grid 4x3
    # ---------------------------------------------------------
    figuras_encontradas = 0
    figuras_faltantes = []

    for idx, (nombre_archivo, titulo) in enumerate(FIGURAS):
        fila = (idx // 3) + 1  # +1 porque fila 0 es el titulo
        col = idx % 3

        ruta = FIGURAS_DIR / nombre_archivo

        if not ruta.exists():
            print(f"  AVISO: no existe {nombre_archivo}")
            figuras_faltantes.append(nombre_archivo)
            continue

        # Cargar imagen
        img = mpimg.imread(ruta)

        # Subplot
        ax = fig.add_subplot(gs[fila, col])
        ax.imshow(img)
        ax.axis("off")

        # Titulo encima de la imagen
        ax.set_title(
            titulo,
            fontsize=11, fontweight="bold",
            color=COLOR_TEXTO, pad=8,
        )

        figuras_encontradas += 1

    # ---------------------------------------------------------
    # Pie de pagina
    # ---------------------------------------------------------
    fig.text(
        0.5, 0.005,
        "Proyecto completo: github.com/jdthgp27/reto5-precios-vivienda-cataluna",
        ha="center", va="bottom", fontsize=10,
        color=COLOR_TEXTO, style="italic",
    )

    # ---------------------------------------------------------
    # Guardar
    # ---------------------------------------------------------
    print(f"\nFiguras insertadas: {figuras_encontradas} / {len(FIGURAS)}")
    if figuras_faltantes:
        print(f"Figuras faltantes: {figuras_faltantes}")

    # PNG
    plt.savefig(SALIDA_PNG, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"\nPNG guardado: {SALIDA_PNG}")
    print(f"Tamano: {SALIDA_PNG.stat().st_size / (1024*1024):.1f} MB")

    # PDF
    plt.savefig(SALIDA_PDF, bbox_inches="tight", facecolor="white")
    print(f"PDF guardado: {SALIDA_PDF}")

    plt.close()

    print("\n" + "=" * 60)
    print("DASHBOARD COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    generar_dashboard()