# 03. Preparación de datos

## 3.1 Pipeline completo

El pipeline de preparación de datos se compone de 3 fases secuenciales,
cada una implementada en un script independiente:

REPARACIÓN src/ingesta/reparar_csv_notariado.py
↓

INGESTA src/ingesta/cargar_notariado.py
↓

AGREGACIÓN src/preparacion/agregar_notariado_barcelona.py
↓

FILTRADO src/preparacion/filtrar_barrios.py
↓

FEATURES src/modelado/01_feature_engineering.py



Cada fase se documenta a continuación.

---

## 3.2 Fase 1: Reparación de CSV corruptos

### Problema

Los 15 CSV descargados de `datos.gob.es` presentaban un formato corrupto:
cada línea estaba rodeada de comillas dobles y las comillas internas
aparecían duplicadas.

**Ejemplo de línea corrupta**:

"2012,1,1,""Ciutat Vella"",1,""el Raval"",9,""No consta"","".."""


**Ejemplo de línea reparada**:

2012,1,1,"Ciutat Vella",1,"el Raval",9,"No consta",..


### Solución

Script: `src/ingesta/reparar_csv_notariado.py`

Algoritmo:
1. Leer cada archivo como texto plano.
2. Para cada línea:
   - Eliminar las comillas exteriores.
   - Reemplazar las comillas duplicadas `""` por comillas simples `"`.
3. Guardar el resultado en `data/raw/notariado_limpio/`.

### Resultado

Los 15 archivos reparados:
- 2012: 1.940 filas
- 2013: 2.121 filas
- 2014: 2.527 filas
- 2015: 2.670 filas
- 2016: 2.837 filas
- 2017: 2.908 filas
- 2018: 2.814 filas
- 2019: 2.811 filas
- 2020: 2.422 filas
- 2021: 2.554 filas
- 2022: 2.703 filas
- 2023: 2.548 filas
- 2024: 2.736 filas
- 2025: 2.733 filas
- 2026: 447 filas (incompleto)

---

## 3.3 Fase 2: Ingesta y consolidación

### Script

`src/ingesta/cargar_notariado.py`

### Procesamiento

Para cada uno de los 15 archivos:
1. Leer el CSV **ignorando la cabecera original** (`skiprows=1`).
2. Asignar nombres fijos a las columnas (`header=None, names=[...]`).
3. Limpiar la columna `num_transacciones` (convertir `".."` y vacíos a 0).
4. Mapear la tipología de uso desde el código numérico.
5. Concatenar todos los archivos en un único DataFrame.

### Decisión metodológica: ignorar cabecera

Se optó por ignorar la cabecera original y asignar nombres fijos porque
algunos CSV tenían problemas residuales en el encabezado tras la
reparación. Esta estrategia es más robusta y reproducible.

### Resultado

**Dataset intermedio**: `data/interim/notariado_barcelona.csv`
- **36.771 filas**
- **10 columnas**
- **15 años** (2012–2026)
- **73 barrios** y **10 distritos**

### Verificación

- Todos los nombres de barrio tienen acentos correctos.
- Los valores de `num_transacciones` son enteros.
- No hay valores nulos en columnas clave.

---

## 3.4 Fase 3: Agregación a nivel barrio-mes

### Script

`src/preparacion/agregar_notariado_barcelona.py`

### Procesamiento

A partir del dataset intermedio, se generan **dos vistas**:

**Vista 1 — Barrio × Mes (total)**
- Agregación por barrio, año y mes.
- Suma de todas las tipologías.
- Target: `total_transacciones`.
- **Relleno de meses faltantes** con 0.

**Vista 2 — Barrio × Mes × Tipología**
- Agregación por barrio, año, mes y tipología.
- Target: `num_transacciones`.
- Sin relleno (solo se registran combinaciones reales).

### Decisión metodológica: excluir tipología "No consta"

La tipología "No consta" (código 9) se ha **excluido del análisis**
porque:
1. Es un cajón de sastre sin valor interpretativo.
2. Aporta ruido al modelo.
3. Representa menos del 5% del total.

### Resultado

**Dataset 1**: `data/processed/barcelona_barrio_mes.csv`
- 11.683 filas
- 73 barrios × 168 meses

**Dataset 2**: `data/processed/barcelona_barrio_mes_tipologia.csv`
- 32.742 filas
- 6 tipologías

---

## 3.5 Fase 4: Filtrado de barrios y meses corruptos

### Script

`src/preparacion/filtrar_barrios.py`

### Filtro 1: Barrios con >90% de ceros

**Criterio**: excluir barrios que tienen **más del 90% de los meses sin
transacciones**.

**Barrios excluidos**:

| Barrio | % ceros | Distrito |
|---|---|---|
| Can Peguera | 100,0% | Nou Barris |
| Vallbona | 100,0% | Nou Barris |
| Torre Baró | 97,6% | Nou Barris |
| Baró de Viver | 97,0% | Sant Andreu |
| la Clota | 92,9% | Horta-Guinardó |

**Justificación**: estos 5 barrios aportan **menos del 1% de las
transacciones totales** y añaden ruido al modelo (predicen 0 casi
siempre).

### Filtro 2: Meses corruptos

**Criterio**: eliminar meses con datos claramente incompletos.

**Meses eliminados**:

**Agosto 2013**: solo 15 transacciones en toda Barcelona (vs ~500 de
media histórica del mismo mes). Solo 2 barrios registraron actividad.
Datos claramente incompletos en la fuente original del Notariado.

**Meses revisados pero NO eliminados**:
- **2012-01 a 2012-05**: valores bajos coherentes con la crisis
  inmobiliaria española de 2012. Datos reales, no errores.
- **2023-10**: 146 transacciones vs mediana ~1.800. Detectado como
  anomalía pero **no eliminado** porque: (1) la caída es del 90%, no
  del 97% como agosto 2013; (2) coincide con incertidumbre política y
  subida de tipos; (3) no hay confirmación de error en la fuente.

### Resultado del filtrado

**Dataset 1**: `data/processed/barcelona_barrio_mes_filtrado.csv`
- **11.356 filas** = 68 barrios × 167 meses
- **68 barrios** (5 menos)
- **167 meses** (1 menos)
- **254.732 transacciones totales**

**Dataset 2**: `data/processed/barcelona_barrio_mes_tipologia_filtrado.csv`
- 32.138 filas

### Verificación

- Todos los barrios tienen exactamente **167 filas** (std=0).
- No hay nulos.
- 10 distritos representados.
- Rango temporal: 2012-01-01 a 2025-12-01.

---

## 3.6 Fase 5: Feature engineering

### Script

`src/modelado/01_feature_engineering.py`

### Features creadas

**Temporales (5)**:
- `mes_sin`, `mes_cos`: codificación cíclica del mes.
- `trimestre`: trimestre del año (1-4).
- `tendencia`: años transcurridos desde 2012.
- `es_agosto`: indicador binario de agosto.

**Lags (5)**:
- `lag_1`, `lag_2`, `lag_3`: transacciones de los 3 meses anteriores.
- `lag_12`: transacciones del mismo mes del año anterior.
- `diff_1`: diferencia entre `lag_1` y `lag_2`.

**Rolling windows (3)**:
- `rolling_3m`, `rolling_6m`, `rolling_12m`: media móvil de 3, 6 y 12
  meses, con shift(1) para evitar leakage.

**Tipologías (6)**:
- `pct_residencial`, `pct_aparcament`, `pct_comercial`, `pct_oficina`,
  `pct_turístic`, `pct_equipaments`: proporción de cada tipología en el
  barrio-mes, **con lag 1** para evitar leakage.

**Contexto (2)**:
- `peso_barrio_en_distrito`: ratio de transacciones del barrio sobre el
  total del distrito, **con lag 1**.
- `peso_barrio_en_ciudad`: ratio del barrio sobre Barcelona, **con lag 1**.

**Codificación categórica (11)**:
- `dist_*`: one-hot encoding de los 10 distritos.
- `barrio_te`: target encoding del barrio (media histórica de
  transacciones, calculada solo sobre train).

### Decisión metodológica: corregir data leakage

**Problema detectado**: las features `peso_barrio_en_distrito` y
`peso_barrio_en_ciudad` se calculaban **con el target del mismo mes**,
lo que generaba **data leakage** (el modelo "veía" parte de la respuesta
correcta durante el entrenamiento).

**Solución**: recalcular todas las features de contexto y tipología con
**lag 1** (mes anterior). Esto garantiza que solo se utiliza información
del pasado.

**Impacto**: el R² de XGBoost cayó de 0,835 (con leakage) a 0,617
(honesto). Este hallazgo se documenta en `docs/decisiones_metodologicas.md`.

### Split temporal

**Criterio**: split **temporal** (no aleatorio) para respetar la
naturaleza secuencial de los datos.

- **Train**: 2012–2022 (11 años) → **8.908 filas**
- **Test**: 2023–2025 (3 años) → **2.448 filas**

### Resultado

**Dataset final**: `data/processed/dataset_modelado.csv`
- **11.356 filas**
- **36 columnas** (target + 3 identificadores + 32 features)

**Train**: `data/processed/train.csv` (8.908 filas)
**Test**: `data/processed/test.csv` (2.448 filas)

---

## 3.7 Resumen del dataset final

### Dimensiones

| Aspecto | Valor |
|---|---|
| Filas totales | 11.356 |
| Columnas | 36 |
| Barrios | 68 |
| Distritos | 10 |
| Meses | 167 |
| Rango temporal | 2012-01 a 2025-12 |
| Train | 8.908 (2012–2022) |
| Test | 2.448 (2023–2025) |

### Distribución del target

| Estadístico | Valor |
|---|---|
| Media | 22,3 |
| Mediana | 16 |
| Std | 23,2 |
| Mín | 0 |
| Máx | 472 |
| Skewness | 2,76 |

### Sin nulos

Tras el feature engineering, **no hay valores nulos** en el dataset
final (los lags iniciales se rellenan con 0).

---

## 3.8 Decisiones metodológicas documentadas

Todas las decisiones tomadas durante la preparación se documentan en
`docs/decisiones_metodologicas.md`:

1. **Ámbito territorial y temporal**.
2. **Filtrado de barrios** (>90% ceros).
3. **Tratamiento de tipologías** (excluir "No consta").
4. **Corrección de meses corruptos** (agosto 2013).
5. **Corrección de data leakage** (features con lag 1).
6. **Split temporal** (2012–2022 vs 2023–2025).

---

## 3.9 Reproducibilidad

Para regenerar el dataset desde cero:

```bash
# 1. Reparar CSV corruptos
python src/ingesta/reparar_csv_notariado.py

# 2. Cargar y consolidar
python src/ingesta/cargar_notariado.py

# 3. Agregar a barrio-mes
python src/preparacion/agregar_notariado_barcelona.py

# 4. Filtrar barrios y meses corruptos
python src/preparacion/filtrar_barrios.py

# 5. Feature engineering
python src/modelado/01_feature_engineering.py

Todo el pipeline tarda menos de 1 minuto en ejecutarse.

Documento generado como parte del Reto 5 — Business Intelligence y Big
Data. Curso Odisea Data, 2025.