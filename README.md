# Predicción de Precios de Vivienda en Cataluña
## Reto 5 · Business Intelligence y Big Data · Curso 6

### Objetivo
Modelo predictivo del **número de transacciones inmobiliarias mensuales
por barrio en Barcelona**, con interpretabilidad vía SHAP y análisis
complementario de alquiler (SERPAVI) y población extranjera (Padrón).

### Resultados principales

| Métrica | Valor |
|---|---|
| Modelo final | XGBoost (objetivo Poisson) |
| R² en test | **0,617** |
| RMSE en test | 15,77 transacciones |
| MAE en test | 9,26 transacciones |
| MAPE | 36,7% |
| Dataset | 68 barrios × 167 meses (2012-2025) |
| Transacciones analizadas | 254.732 |

### Hallazgos clave

1. **Ciclo completo 2012-2025**: crisis, recuperación, COVID, máximos.
2. **La tendencia histórica del barrio** es el factor más predictivo
   (`rolling_12m` con 23,7% del impacto SHAP).
3. **El alquiler NO predice transacciones** (correlación nula, r=-0,07).
4. **La población extranjera es mayoritariamente inquilina** (70,5%).
5. **El modelo subestima picos extremos** (>100 transacciones).

### Fuentes de datos

| Fuente | Uso | Granularidad |
|---|---|---|
| [datos.gob.es](https://datos.gob.es) (Notariado) | Fuente principal | Barrio × mes × tipología |
| SERPAVI (Ministerio Vivienda) | Análisis de alquiler | Distrito (agregable a barrio) |
| Padrón Municipal 2024 | Análisis de extranjeros | Distrito |

### Stack tecnológico

- **Python 3.13**
- pandas, numpy
- scikit-learn (Ridge, Lasso, TimeSeriesSplit)
- **XGBoost** (modelo final, objetivo Poisson)
- **SHAP** (interpretabilidad)
- matplotlib, seaborn (visualizaciones)
- python-pptx (presentaciones)

### Estructura del proyecto


```text
data/
├── raw/ → datos originales (Notariado, SERPAVI)
├── interim/ → datos consolidados
└── processed/ → datasets listos para modelar

notebooks/ → exploración (Jupyter)

src/
├── ingesta/ → carga y consolidación
├── preparacion/ → agregación, filtrado
├── analisis/ → EDA y análisis complementario
├── modelado/ → feature engineering, baseline, XGBoost, SHAP
├── presentacion/ → generación de PPTX
└── utilidades/ → config, logger

models/ → modelos entrenados (XGBoost, Ridge)

reports/
├── figuras/ → 26 visualizaciones PNG
├── documentacion/ → 6 documentos del proyecto
├── presentacion/ → 2 presentaciones PPTX
└── metricas/ → tablas comparativas CSV

docs/ → decisiones metodológicas, autoevaluación
```


text


### Documentación

| # | Documento | Descripción |
|---|---|---|
| 01 | [Definición del problema](reports/documentacion/01_definicion_problema.md) | Business problem y objetivos |
| 02 | [Fuentes de datos](reports/documentacion/02_fuentes_datos.md) | Notariado, SERPAVI, Padrón |
| 03 | [Preparación de datos](reports/documentacion/03_preparacion_datos.md) | Pipeline de 5 fases |
| 04 | [Análisis exploratorio](reports/documentacion/04_analisis_exploratorio.md) | EDA con 8 figuras |
| 05 | [Modelado y evaluación](reports/documentacion/05_modelado_evaluacion.md) | Baseline + XGBoost + SHAP |
| 06 | [Conclusiones y recomendaciones](reports/documentacion/06_conclusiones_recomendaciones.md) | Recomendaciones por perfil |

Documentos adicionales:
- [Decisiones metodológicas](docs/decisiones_metodologicas.md)
- [Autoevaluación del reto](docs/autoevaluacion.md)
- [Índice de visualizaciones](reports/visualizaciones.md)

### Visualizaciones

26 figuras organizadas por temática:
- **8 EDA**: serie temporal, estacionalidad, ranking, tipologías.
- **6 Modelado**: baseline, XGBoost, residuos.
- **5 SHAP**: summary, bar, dependence, waterfall, heatmap.
- **2 SERPAVI**: alquiler vs transacciones, evolución.
- **5 Extranjeros**: alquiler, compraventas, compradores, población.

Ver [índice completo](reports/visualizaciones.md).

### Presentaciones

- [**Presentación 1: Metodología**](reports/presentacion/presentacion_1_metodologia.pptx)
  (14 slides) — pipeline técnico
- [**Presentación 2: Resultados**](reports/presentacion/presentacion_2_resultados.pptx)
  (17 slides) — hallazgos e interpretación

### Reproducibilidad

```bash
# 1. Clonar repositorio
git clone https://github.com/jdthgp27/reto5-precios-vivienda-cataluna.git
cd reto5-precios-vivienda-cataluna

# 2. Crear entorno virtual
python -m venv venv
source venv/Scripts/activate  # Git Bash en Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar pipeline completo
python src/ingesta/reparar_csv_notariado.py
python src/ingesta/cargar_notariado.py
python src/preparacion/agregar_notariado_barcelona.py
python src/preparacion/filtrar_barrios.py
python src/modelado/01_feature_engineering.py
python src/modelado/02_baseline.py
python src/modelado/03_xgboost.py
python src/modelado/04_evaluacion.py
python src/modelado/05_shap.py
```
```text
Tiempo total: < 5 minutos.

Entregables del reto
☑ 1. Código y scripts documentados (src/)
☑ 2. Documentación completa (reports/documentacion/)
☑ 3. Visualizaciones (reports/figuras/)
☑ 4. Presentación ejecutiva (reports/presentacion/)
Trabajo futuro
Integrar Idescat: añadir población y renta por barrio.

Integrar SERPAVI a nivel de barrio: calcular elasticidad
alquiler-compraventa.

Modelo hurdle (zero-inflated): mejorar predicción de picos.

Expandir a Madrid y otras ciudades.

Proyecto académico · Odisea Data · 2025
```