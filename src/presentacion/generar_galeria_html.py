# generar_galeria_html.py
# Genera una galeria HTML navegable con todas las figuras del proyecto.
#
# Uso:
#   python src/presentacion/generar_galeria_html.py
#
# Salida:
#   reports/dashboard.html

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.utilidades.config import BASE_DIR, FIGURAS_DIR


SALIDA_HTML = BASE_DIR / "reports" / "dashboard.html"


# ============================================================
# ESTRUCTURA DE SECCIONES
# ============================================================
SECCIONES = [
    {
        "id": "eda",
        "titulo": "1. Análisis Exploratorio (EDA)",
        "descripcion": "Patrones temporales, espaciales y estacionales del mercado inmobiliario.",
        "figuras": [
            ("01_serie_temporal_global.png",
             "Evolución mensual de transacciones 2012-2025",
             "Ciclo completo: crisis (2012), recuperación (2014-2019), COVID (2020), máximos (2025)."),
            ("02_boxplot_estacionalidad.png",
             "Distribución de transacciones por mes",
             "Julio es el mes de mayor actividad; agosto el de menor."),
            ("03_heatmap_anio_mes.png",
             "Heatmap año × mes",
             "Visualización de la estacionalidad año por año."),
            ("04_ranking_barrios.png",
             "Top 15 / Bottom 15 barrios",
             "Sant Gervasi-Galvany lidera con 11.086 transacciones."),
            ("05_tipologia_porcentual.png",
             "Evolución porcentual por tipología",
             "67% residencial, 28% aparcamiento."),
            ("06_tipologia_absoluta_no_residencial.png",
             "Tipologías no residenciales",
             "Evolución del comercial, oficina y turístico."),
            ("07_heatmap_barrio_anio.png",
             "Índice barrio × año (2012=100)",
             "Crecimiento desigual entre barrios."),
            ("08_distribucion_target.png",
             "Distribución del target",
             "Skewness = 2,76 → justifica modelo Poisson."),
        ],
    },
    {
        "id": "modelado",
        "titulo": "2. Modelado",
        "descripcion": "Comparativa baseline (Ridge/Lasso) vs XGBoost y análisis de residuos.",
        "figuras": [
            ("09_comparativa_baseline.png",
             "Comparativa de modelos baseline",
             "Dummy, Ridge y Lasso con 15 features."),
            ("10_xgboost_importancia.png",
             "Feature importance (XGBoost nativo)",
             "Ranking de importancia por número de splits."),
            ("11_xgboost_predicciones.png",
             "Predicciones vs valores reales",
             "Scatter + análisis de residuos."),
            ("12_analisis_residuos.png",
             "Distribución de residuos",
             "Asimetría 4,22 · Kurtosis 52,04."),
            ("13_residuos_por_barrio.png",
             "Residuos por barrio (MAPE)",
             "Peor: la Vila Olímpica del Poblenou. Mejor: el Poble Sec."),
            ("14_residuos_por_mes.png",
             "Residuos por mes (MAPE y sesgo)",
             "Peor mes: octubre (incluye 2023 atípico)."),
        ],
    },
    {
        "id": "shap",
        "titulo": "3. Interpretabilidad (SHAP)",
        "descripcion": "Análisis de qué variables influyen más en el modelo y cómo lo hacen.",
        "figuras": [
            ("15_shap_summary.png",
             "SHAP Summary Plot (beeswarm)",
             "Distribución de impactos de cada feature."),
            ("16_shap_bar.png",
             "SHAP Feature Importance",
             "Top: rolling_12m (0,278), barrio_te (0,156)."),
            ("17_shap_dependence_top3.png",
             "SHAP Dependence (top 3)",
             "Relación entre features y predicción."),
            ("18_shap_waterfall.png",
             "SHAP Waterfall",
             "Explicación del peor caso: Marina del Prat Vermell."),
            ("19_shap_heatmap.png",
             "Correlación entre SHAP values",
             "Interacciones entre features."),
        ],
    },
    {
        "id": "serpavi",
        "titulo": "4. Análisis complementario: SERPAVI",
        "descripcion": "Cruce del precio del alquiler con el volumen de transacciones.",
        "figuras": [
            ("20_serpavi_vs_transacciones.png",
             "Alquiler €/m² vs transacciones",
             "Correlación nula: r=-0,07 (p=0,85)."),
            ("21_serpavi_evolucion.png",
             "Evolución del alquiler por distrito",
             "Serie 2015-2024 (SERPAVI)."),
        ],
    },
    {
        "id": "extranjeros",
        "titulo": "5. Análisis complementario: extranjeros",
        "descripcion": "Población extranjera, compradores y estimación de inquilinos por distrito.",
        "figuras": [
            ("22_alquiler_por_distrito.png",
             "Precio del alquiler por distrito",
             "Ciutat Vella lidera con 15,55 €/m²/mes."),
            ("23_compraventas_por_distrito.png",
             "Compraventas por distrito (2024)",
             "Eixample lidera con 4.425 transacciones."),
            ("24_compradores_extranjeros.png",
             "% compradores extranjeros",
             "Ciutat Vella: 42,6% · Media BCN: 23%."),
            ("25_poblacion_extranjera.png",
             "% población extranjera",
             "Ciutat Vella: 63,7%."),
            ("26_inquilinos_extranjeros_estimado.png",
             "Estimación de inquilinos extranjeros",
             "Fórmula: población extranjera × 70,5%."),
        ],
    },
]


# ============================================================
# PLANTILLA HTML
# ============================================================
def generar_html():
    print("=" * 60)
    print("GENERANDO GALERIA HTML")
    print("=" * 60)

    html = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard · Predicción de Transacciones Inmobiliarias Barcelona</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #ffffff;
    color: #2C3E50;
    line-height: 1.6;
  }
  header {
    background: linear-gradient(135deg, #2E86AB 0%, #1e5f7a 100%);
    color: white;
    padding: 60px 40px;
    text-align: center;
  }
  header h1 { font-size: 2.5em; margin-bottom: 15px; }
  header p { font-size: 1.1em; opacity: 0.95; }
  .metricas {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 30px;
    margin-top: 30px;
  }
  .metrica {
    background: rgba(255,255,255,0.15);
    padding: 15px 25px;
    border-radius: 8px;
    backdrop-filter: blur(10px);
  }
  .metrica .valor { font-size: 1.8em; font-weight: bold; display: block; }
  .metrica .etiqueta { font-size: 0.85em; opacity: 0.9; }

  nav {
    background: #f8f9fa;
    border-bottom: 1px solid #e0e0e0;
    padding: 15px 40px;
    position: sticky;
    top: 0;
    z-index: 100;
  }
  nav ul { display: flex; list-style: none; gap: 30px; flex-wrap: wrap; justify-content: center; }
  nav a {
    color: #2E86AB;
    text-decoration: none;
    font-weight: 600;
    padding: 5px 10px;
    border-radius: 4px;
    transition: background 0.2s;
  }
  nav a:hover { background: #e8f4f8; }

  main { padding: 40px; max-width: 1400px; margin: 0 auto; }
  section { margin-bottom: 60px; }
  section h2 {
    color: #2E86AB;
    font-size: 1.8em;
    border-bottom: 3px solid #2E86AB;
    padding-bottom: 10px;
    margin-bottom: 10px;
  }
  section > p.descripcion {
    color: #666;
    font-size: 1em;
    margin-bottom: 30px;
    font-style: italic;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
    gap: 25px;
  }
  .figura {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  }
  .figura:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 20px rgba(46,134,171,0.15);
  }
  .figura img { width: 100%; height: auto; display: block; }
  .figura .info {
    padding: 18px;
    border-top: 1px solid #f0f0f0;
  }
  .figura .info h3 {
    font-size: 1em;
    color: #2E86AB;
    margin-bottom: 6px;
  }
  .figura .info p {
    font-size: 0.88em;
    color: #666;
    margin: 0;
  }

  footer {
    background: #2C3E50;
    color: white;
    text-align: center;
    padding: 30px;
    margin-top: 60px;
  }
  footer a { color: #F18F01; text-decoration: none; }
  footer a:hover { text-decoration: underline; }

  @media (max-width: 600px) {
    header h1 { font-size: 1.6em; }
    .grid { grid-template-columns: 1fr; }
    nav ul { gap: 15px; }
    main { padding: 20px; }
  }
</style>
</head>
<body>

<header>
  <h1>Predicción de Transacciones Inmobiliarias</h1>
  <p>Barcelona 2012–2025 · Reto 5 · Business Intelligence y Big Data</p>
  <div class="metricas">
    <div class="metrica"><span class="valor">0,617</span><span class="etiqueta">R² test</span></div>
    <div class="metrica"><span class="valor">15,77</span><span class="etiqueta">RMSE</span></div>
    <div class="metrica"><span class="valor">68</span><span class="etiqueta">barrios</span></div>
    <div class="metrica"><span class="valor">254.732</span><span class="etiqueta">transacciones</span></div>
    <div class="metrica"><span class="valor">26</span><span class="etiqueta">visualizaciones</span></div>
  </div>
</header>

<nav>
  <ul>
"""

    # Navegacion
    for sec in SECCIONES:
        html += f'    <li><a href="#{sec["id"]}">{sec["titulo"]}</a></li>\n'

    html += """  </ul>
</nav>

<main>
"""

    # Secciones
    total_figuras = 0
    figuras_faltantes = []

    for sec in SECCIONES:
        html += f'<section id="{sec["id"]}">\n'
        html += f'  <h2>{sec["titulo"]}</h2>\n'
        html += f'  <p class="descripcion">{sec["descripcion"]}</p>\n'
        html += '  <div class="grid">\n'

        for nombre, titulo, descripcion in sec["figuras"]:
            ruta = FIGURAS_DIR / nombre
            if not ruta.exists():
                figuras_faltantes.append(nombre)
                continue

            html += '    <div class="figura">\n'
            html += f'      <img src="figuras/{nombre}" alt="{titulo}" loading="lazy">\n'
            html += '      <div class="info">\n'
            html += f'        <h3>{titulo}</h3>\n'
            html += f'        <p>{descripcion}</p>\n'
            html += '      </div>\n'
            html += '    </div>\n'
            total_figuras += 1

        html += '  </div>\n'
        html += '</section>\n\n'

    # Footer
    html += """
</main>

<footer>
  <p><strong>Proyecto completo</strong> · Reto 5 · Odisea Data 2025</p>
  <p>Repositorio: <a href="https://github.com/jdthgp27/reto5-precios-vivienda-cataluna">github.com/jdthgp27/reto5-precios-vivienda-cataluna</a></p>
  <p style="opacity:0.7; font-size:0.85em; margin-top:10px;">Modelo XGBoost (objetivo Poisson) · 32 features · Train 2012-2022 / Test 2023-2025</p>
</footer>

</body>
</html>
"""

    # Guardar
    SALIDA_HTML.parent.mkdir(parents=True, exist_ok=True)
    with open(SALIDA_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nFiguras insertadas: {total_figuras}")
    if figuras_faltantes:
        print(f"Figuras faltantes: {figuras_faltantes}")
    print(f"\nHTML guardado: {SALIDA_HTML}")
    print(f"Tamano: {SALIDA_HTML.stat().st_size / 1024:.1f} KB")

    print("\n" + "=" * 60)
    print("GALERIA HTML COMPLETADA")
    print("=" * 60)
    print(f"\nAbre la galeria en el navegador:")
    print(f"  start {SALIDA_HTML}")


if __name__ == "__main__":
    generar_html()