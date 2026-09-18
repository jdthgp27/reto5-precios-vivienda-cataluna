# 05. Modelado y evaluación

## 5.1 Objetivo

Construir y evaluar un modelo predictivo del **número de transacciones
inmobiliarias mensuales por barrio** en Barcelona, comparando un baseline
lineal con un modelo avanzado (XGBoost).

---

## 5.2 Estrategia de validación

### Split temporal

**Decisión**: split **temporal** (no aleatorio).

- **Train**: 2012–2022 → 8.908 filas
- **Test**: 2023–2025 → 2.448 filas

**Justificación**: el objetivo es predecir el futuro, por lo que el
modelo debe evaluarse en datos posteriores a los de entrenamiento.
Un split aleatorio causaría **data leakage temporal** (usar datos
futuros para predecir el presente).

### Métricas

| Métrica | Descripción | Objetivo |
|---|---|---|
| **RMSE** | Raíz del error cuadrático medio | Minimizar |
| **MAE** | Error absoluto medio | Minimizar |
| **R²** | Coeficiente de determinación | Maximizar |
| **MAPE** | Error porcentual absoluto medio | Minimizar |

---

## 5.3 Baseline: Ridge y Lasso

### Script

`src/modelado/02_baseline.py`

### Features del baseline (15)

Se seleccionaron **solo features numéricas** para el baseline:


Mes, Any, mes_sin, mes_cos, es_agosto, tendencia,
lag_1, lag_2, lag_3, lag_12,
rolling_3m, rolling_6m, rolling_12m, diff_1, barrio_te


### Modelos evaluados

**1. Dummy (media)**: predice siempre la media del train.

**2. Dummy (media por barrio)**: predice la media histórica del barrio.

**3. Ridge**: regresión lineal con regularización L2.

**4. Lasso**: regresión lineal con regularización L1.

### Optimización de hiperparámetros

- **TimeSeriesSplit** con 3 folds.
- **GridSearchCV** sobre el parámetro `alpha`:
  - Ridge: `[0.01, 0.1, 1.0, 10.0, 100.0]`
  - Lasso: `[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]`

### Resultados

| Modelo | RMSE | MAE | R² | MAPE |
|---|---|---|---|---|
| Dummy (media) | 26,53 | 18,25 | **−0,08** | 66,0% |
| Dummy (media barrio) | 19,23 | 12,36 | 0,431 | 47,2% |
| **Ridge** | **15,82** | 9,73 | **0,615** | 43,9% |
| Lasso | 16,02 | 9,72 | 0,605 | 41,9% |

### Análisis

- **Dummy (media) tiene R² negativo (−0,08)**: predecir la media global
  es **peor que no hacer nada** porque el test tiene otra distribución
  (2023–2025 tiene más actividad que 2012–2022).
- **Dummy (media por barrio) mejora a R²=0,43**: la identidad del barrio
  explica gran parte de la varianza.
- **Ridge bate al baseline por +0,18 de R²**: captura estacionalidad,
  lags y tendencia.
- **Lasso ≈ Ridge**: empate técnico.

**Mejor modelo baseline: Ridge con R²=0,615, RMSE=15,82**.

---

## 5.4 Modelo final: XGBoost

### Script

`src/modelado/03_xgboost.py`

### Features (32)

Todas las features del dataset, excepto `Any`, `Mes`, `Nom_Barri` y
`total_transacciones`:

- 5 temporales
- 5 lags
- 3 rolling
- 6 tipologías (con lag 1)
- 2 contexto (con lag 1)
- 10 distritos (one-hot)
- 1 target encoding de barrio

### Configuración

- **Objetivo**: `count:poisson` (adecuado para datos de conteo).
- **Tree method**: `hist` (rápido y preciso).
- **Búsqueda de hiperparámetros**: `RandomizedSearchCV` con
  `TimeSeriesSplit(n_splits=3)`.
- **Grid**: conservador para evitar overfitting.

### Hiperparámetros óptimos

| Parámetro | Valor |
|---|---|
| `n_estimators` | 200 |
| `max_depth` | 3 |
| `learning_rate` | 0,03 |
| `subsample` | 0,8 |
| `colsample_bytree` | 0,7 |
| `reg_alpha` | 1,0 |
| `reg_lambda` | 20,0 |
| `min_child_weight` | 10 |

**Nota**: los hiperparámetros son **deliberadamente conservadores**
(max_depth bajo, reg_lambda alto) para evitar overfitting.

### Resultados

| Métrica | Train | Test | Delta |
|---|---|---|---|
| RMSE | 13,39 | **15,77** | +2,38 |
| MAE | 7,43 | **9,26** | +1,83 |
| **R²** | 0,639 | **0,617** | −0,022 |
| MAPE | — | **36,7%** | — |

### Comparativa final

| Modelo | RMSE | MAE | R² | MAPE |
|---|---|---|---|---|
| Dummy (media) | 26,53 | 18,25 | −0,08 | 66,0% |
| Dummy (barrio) | 19,23 | 12,36 | 0,431 | 47,2% |
| Ridge | 15,82 | 9,73 | 0,615 | 43,9% |
| Lasso | 16,02 | 9,72 | 0,605 | 41,9% |
| **XGBoost** | **15,77** | **9,26** | **0,617** | **36,7%** |

### Decisión: XGBoost como modelo final

Aunque la mejora sobre Ridge es **marginal** (RMSE −0,3%, R² +0,002),
se elige XGBoost por:

1. **Ligera mejora en RMSE y MAPE**.
2. **Overfitting controlado** (delta train-test R² = 0,022).
3. **Capacidad de capturar interacciones no lineales**.
4. **Interpretabilidad superior vía SHAP** (dependence plots,
   waterfall, interacciones).

**Documentación honesta**: se reconoce que la diferencia es pequeña,
lo que sugiere que las relaciones son **mayormente lineales**. Se
documenta como limitación metodológica.

---

## 5.5 Data leakage: detección y corrección

### Problema detectado

En la primera versión del feature engineering, las features
`peso_barrio_en_distrito` y `peso_barrio_en_ciudad` se calculaban
**con el target del mismo mes**:

```python
peso_barrio_en_distrito = total_transacciones_barrio / total_transacciones_distrito

Esto generaba data leakage: el modelo veía parte de la respuesta
durante el entrenamiento.

Síntomas
R² inusualmente alto: 0,835 en test.

Feature importance sospechosa: peso_barrio_en_ciudad con 24%
de importancia.

MAPE muy bajo: 23,8%.

Diagnóstico
Se identificaron las dos features con leakage y se documentó el
problema. También se detectó que las features pct_* (tipologías)
tenían leakage parcial (se calculaban con datos del mismo mes).

Solución
Recalcular todas las features de contexto y tipología con lag 1
(mes anterior):

python
peso_barrio_en_distrito = ratio.shift(1)
pct_residencial = pct.shift(1)

Impacto
Métrica	Con leakage	Sin leakage (honesto)
R² test	0,835	0,617
RMSE test	10,34	15,77
MAPE	23,8%	36,7%
El rendimiento cayó, pero el modelo es HONESTO. Esta corrección es
un hallazgo metodológico clave del proyecto.

5.6 Análisis de residuos
Script
src/modelado/04_evaluacion.py

Distribución de residuos

Figura: 12_analisis_residuos.png

Estadístico	Valor
Media	+1,889
Std	15,660
Asimetría	4,221
Kurtosis	52,037
Interpretación: los residuos están fuertemente sesgados y tienen
colas muy pesadas. Esto indica que hay outliers que el modelo
no captura bien (picos de transacciones en barrios concretos).

Residuos por barrio
Figura: 13_residuos_por_barrio.png

Peor barrio (MAPE): la Vila Olímpica del Poblenou (60,7%).

Mejor barrio (MAPE): el Poble Sec (18,5%).

Insight: el modelo falla más en barrios con alta volatilidad
(grandes operaciones puntuales, nueva construcción).

Residuos por mes
Figura: 14_residuos_por_mes.png

Peor mes (MAPE): octubre (83,7%).

Mejor mes (MAPE): marzo (25,6%).

Insight: octubre tiene MAPE muy alto porque incluye el mes corrupto
de 2023 (no eliminado, solo documentado).

Residuos por magnitud
Figura: 12_analisis_residuos.png (gráfico residual vs predicción)

Rango	N	MAPE	Sesgo	Interpretación
0-5	285	—	−8,56	Sobreestima fuerte
5-15	551	72,1%	−4,66	Sobreestima
15-30	712	25,8%	−0,78	Casi perfecto
30-60	629	22,2%	+4,70	Subestima
60-100	228	25,1%	+19,0	Subestima fuerte
100+	43	51,8%	+67,5	Subestima brutal
Insight: el modelo es un "regresor a la media". Cuando el
valor real es bajo, sobreestima; cuando es alto, subestima. Este es
el problema clásico de los árboles de decisión con distribuciones
sesgadas.

Implicación de negocio: el modelo es útil para predicciones
"típicas" (15-60 transacciones), pero no captura picos extremos.

5.7 Interpretabilidad: SHAP
Script
src/modelado/05_shap.py

Análisis realizados
Summary plot (beeswarm): 15_shap_summary.png

Bar plot (importancia media): 16_shap_bar.png

Dependence plots (top 3): 17_shap_dependence_top3.png

Waterfall plot (caso individual): 18_shap_waterfall.png

Heatmap de correlaciones SHAP: 19_shap_heatmap.png


Top 20 features por SHAP
Rank	Feature	Impacto medio
1	rolling_12m	0,278
2	barrio_te	0,156
3	rolling_6m	0,097
4	es_agosto	0,095
5	lag_1	0,046
6	rolling_3m	0,039
7	mes_cos	0,029
8	lag_12	0,025
9	tendencia	0,017
10	peso_barrio_en_ciudad	0,017
11	pct_residencial	0,015
12	mes_sin	0,011
13	trimestre	0,002
14	peso_barrio_en_distrito	0,001
15	diff_1	0,0002
Hallazgos clave
1. rolling_12m es la feature más importante (23,7% del impacto)

El modelo es un "extrapolador de tendencia": la media móvil de 12
meses determina en gran medida las predicciones.

2. barrio_te es la segunda (13,3%)

La identidad del barrio es clave: Sant Gervasi no se comporta como
la Clota.

3. es_agosto es sorprendentemente alto (8,1%)

El modelo aprendió que agosto es especial y ajusta las predicciones.

4. Los lags cortos (lag_1, lag_2, lag_3) importan poco

Si ya tienes rolling_12m, los lags individuales aportan poco marginal.

5. La corrección del leakage cambió el ranking

Antes (con leakage), peso_barrio_en_ciudad dominaba. Ahora, cae al
puesto 10 con impacto 0,017.

Caso waterfall
Caso seleccionado: la Marina del Prat Vermell, julio 2025.

Valor	Resultado
Real	296
Predicción	15,5
Residuo	280,5
Insight: el modelo no puede predecir este pico. El barrio tiene
historia de baja actividad, y el rolling_12m tira hacia abajo. La
predicción es 15,5 cuando la realidad es 296.

Implicación: para barrios en desarrollo urbanístico, el modelo
necesita información adicional (obras en curso, licencias).

5.8 Conclusiones del modelado
Sobre el rendimiento
Ridge (baseline) es sorprendentemente competitivo: R²=0,615,
RMSE=15,82.

XGBoost mejora marginalmente: R²=0,617, RMSE=15,77.

La diferencia es pequeña, lo que sugiere que las relaciones son
mayormente lineales.

Se elige XGBoost por su interpretabilidad SHAP y su capacidad
de capturar interacciones.

Sobre las limitaciones
Subestima valores altos: en el rango 100+ el MAE es 67,5.

Sobreestima valores bajos: en el rango 0-5 sobreestima por 8,56.

No captura picos: el modelo no puede predecir eventos extremos.

Residuos sesgados: skewness 4,22, kurtosis 52,04.

Sobre las mejoras futuras
Integrar Idescat (población, renta) para añadir contexto.

Integrar SERPAVI a nivel de barrio (agregando secciones
censales).

Usar un modelo hurdle (zero-inflated) para separar el problema
en dos: predecir si habrá transacciones y cuántas.

Añadir features de obra nueva (licencias, visados).

Documento generado como parte del Reto 5 — Business Intelligence y Big
Data. Curso Odisea Data, 2025.

