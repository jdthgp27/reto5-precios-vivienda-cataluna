# Índice de visualizaciones

Este documento recoge las **26 visualizaciones** generadas en el proyecto,
organizadas por temática.

## 1. Análisis exploratorio (EDA)

| # | Archivo | Descripción | Documento |
|---|---|---|---|
| 01 | `01_serie_temporal_global.png` | Evolución mensual de transacciones 2012-2025 | Doc 04 |
| 02 | `02_boxplot_estacionalidad.png` | Distribución de transacciones por mes | Doc 04 |
| 03 | `03_heatmap_anio_mes.png` | Heatmap año × mes de transacciones | Doc 04 |
| 04 | `04_ranking_barrios.png` | Top 15 / Bottom 15 barrios por transacciones | Doc 04 |
| 05 | `05_tipologia_porcentual.png` | Evolución porcentual por tipología | Doc 04 |
| 06 | `06_tipologia_absoluta_no_residencial.png` | Tipologías no residenciales (absoluto) | Doc 04 |
| 07 | `07_heatmap_barrio_anio.png` | Índice normalizado barrio × año (2012=100) | Doc 04 |
| 08 | `08_distribucion_target.png` | Distribución del target (histograma + log) | Doc 04 |

## 2. Modelado

| # | Archivo | Descripción | Documento |
|---|---|---|---|
| 09 | `09_comparativa_baseline.png` | Comparativa Dummy / Ridge / Lasso | Doc 05 |
| 10 | `10_xgboost_importancia.png` | Feature importance (XGBoost nativo) | Doc 05 |
| 11 | `11_xgboost_predicciones.png` | Predicciones vs reales + residuos | Doc 05 |
| 12 | `12_analisis_residuos.png` | Distribución de residuos + QQ-plot | Doc 05 |
| 13 | `13_residuos_por_barrio.png` | Top/bottom barrios por MAPE | Doc 05 |
| 14 | `14_residuos_por_mes.png` | MAPE y sesgo por mes | Doc 05 |

## 3. Interpretabilidad (SHAP)

| # | Archivo | Descripción | Documento |
|---|---|---|---|
| 15 | `15_shap_summary.png` | Beeswarm plot con todas las features | Doc 05 |
| 16 | `16_shap_bar.png` | Importancia media SHAP | Doc 05 |
| 17 | `17_shap_dependence_top3.png` | Dependence plots top 3 features | Doc 05 |
| 18 | `18_shap_waterfall.png` | Waterfall de un caso individual | Doc 05 |
| 19 | `19_shap_heatmap.png` | Correlación entre SHAP values | Doc 05 |

## 4. Análisis complementario: SERPAVI

| # | Archivo | Descripción | Documento |
|---|---|---|---|
| 20 | `20_serpavi_vs_transacciones.png` | Alquiler €/m² vs transacciones por distrito | Doc 02 |
| 21 | `21_serpavi_evolucion.png` | Evolución del alquiler por distrito 2015-2024 | Doc 02 |

## 5. Análisis complementario: extranjeros

| # | Archivo | Descripción | Documento |
|---|---|---|---|
| 22 | `22_alquiler_por_distrito.png` | Precio alquiler por distrito (barras) | Doc 02 |
| 23 | `23_compraventas_por_distrito.png` | Compraventas por distrito (barras) | Doc 02 |
| 24 | `24_compradores_extranjeros.png` | % compradores extranjeros por distrito | Doc 02 |
| 25 | `25_poblacion_extranjera.png` | % población extranjera por distrito | Doc 02 |
| 26 | `26_inquilinos_extranjeros_estimado.png` | Estimación % inquilinos extranjeros | Doc 02 |

## Resumen

| Categoría | Nº figuras |
|---|---|
| EDA | 8 |
| Modelado | 6 |
| SHAP | 5 |
| SERPAVI | 2 |
| Extranjeros | 5 |
| **Total** | **26** |

Todas las figuras están en `reports/figuras/`.