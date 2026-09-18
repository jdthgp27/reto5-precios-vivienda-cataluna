# 04. Análisis exploratorio de datos (EDA)

## 4.1 Objetivo

El análisis exploratorio tiene como objetivo **comprender la estructura
y los patrones** del dataset antes de construir el modelo predictivo.

Se estructura en 6 bloques temáticos, cada uno con sus visualizaciones
y hallazgos.

---

## 4.2 Bloque 1: Serie temporal global

**Figura**: `01_serie_temporal_global.png`

### Descripción

Serie mensual del total de transacciones en Barcelona (2012–2025), con:
- Línea azul: transacciones mensuales.
- Línea roja discontinua: media móvil de 12 meses.
- Banda roja sombreada: período COVID (marzo–junio 2020).
- Línea verde punteada: inicio de 2022.

### Hallazgos

**Total de transacciones 2012–2025**: 254.732

**Máximo mensual**: julio 2025 (3.041 transacciones)

**Mínimo mensual**: agosto 2013 (15 transacciones) — eliminado del
dataset por datos corruptos (ver documento 03).

**Fases identificadas**:

| Período | Descripción |
|---|---|
| 2012–2013 | Fondo de la crisis inmobiliaria |
| 2014–2017 | Recuperación sostenida (+45% anual) |
| 2018–2019 | Estabilización (~20.000 anuales) |
| 2020 | Caída COVID (−30% anual) |
| 2021–2025 | Rebote y máximos históricos |

**Insight**: el mercado inmobiliario de Barcelona ha pasado por un ciclo
completo en 14 años, con una caída severa en 2012 y 2020, y una
recuperación sostenida desde 2021.

---

## 4.3 Bloque 2: Estacionalidad

**Figuras**:
- `02_boxplot_estacionalidad.png`
- `03_heatmap_anio_mes.png`

### Descripción

**Boxplot mensual**: distribución de las transacciones totales por mes
(agregando todos los años).

**Heatmap año × mes**: cada celda es el total de transacciones de un
mes concreto de un año concreto.

### Hallazgos

**Mes con MÁS actividad media**: **julio**

**Mes con MENOS actividad media**: **agosto**

**Patrón estacional**:
- **Primavera (marzo–junio)**: actividad creciente.
- **Verano (julio–agosto)**: julio es el pico máximo, agosto cae
  drásticamente.
- **Otoño (septiembre–diciembre)**: recuperación.

**Insight**: el pico de julio es contraintuitivo respecto a la creencia
común de que agosto es el mes más activo para el turismo. Esto se debe
a que **las escrituras se firman con semanas de retraso** respecto a la
operación real, y julio concentra muchas firmas antes del parón
veraniego.

---

## 4.4 Bloque 3: Ranking de barrios

**Figura**: `04_ranking_barrios.png`

### Descripción

Dos gráficos de barras horizontales:
- **Top 15 barrios** por transacciones totales (2012–2025).
- **Bottom 15 barrios** por transacciones totales.

### Hallazgos

**Top 5 barrios**:

| Barrio | Distrito | Transacciones |
|---|---|---|
| Sant Gervasi - Galvany | Sarrià-Sant Gervasi | 11.086 |
| la Nova Esquerra de l'Eixample | Eixample | 10.550 |
| la Dreta de l'Eixample | Eixample | 9.900 |
| Sant Andreu | Sant Andreu | 8.934 |
| la Sagrada Família | Eixample | 8.534 |

**Bottom 5 barrios**:

| Barrio | Distrito |
|---|---|
| Vallvidrera, el Tibidabo i les Planes | Sarrià-Sant Gervasi |
| la Verneda i la Pau | Sant Martí |
| Canyelles | Nou Barris |
| la Marina del Prat Vermell | Sants-Montjuïc |
| el Parc i la Llacuna del Poblenou | Sant Martí |

**Insight**: los barrios con más transacciones son **grandes, céntricos
y con alta rotación** (Eixample, Sant Gervasi, Sant Andreu). Los barrios
del bottom son **periféricos o de baja densidad** (Vallvidrera, Canyelles,
la Verneda).

---

## 4.5 Bloque 4: Evolución por tipología

**Figuras**:
- `05_tipologia_porcentual.png`
- `06_tipologia_absoluta_no_residencial.png`

### Descripción

**Stacked area (porcentual)**: evolución de la proporción de cada
tipología sobre el total de transacciones.

**Líneas absolutas**: evolución del número de transacciones para las
tipologías no residenciales.

### Hallazgos

**Distribución por tipología (2012–2025)**:

| Tipología | Transacciones | % |
|---|---|---|
| **Residencial** | **168.670** | **66,7%** |
| Aparcament | 71.048 | 28,1% |
| Comercial | 8.439 | 3,3% |
| Oficina | 3.547 | 1,4% |
| Turístic | 883 | 0,3% |
| Equipaments | 253 | 0,1% |

**Insight**: el **67% de las transacciones son residenciales**, pero hay
un **28% de aparcamientos**, lo cual es característico de Barcelona:
muchas operaciones incluyen plaza de garaje como transacción separada.

Las tipologías no residenciales (turístico, comercial, oficinas) tienen
**mucha menos representación**, aunque el turístico ha crecido en los
últimos años.

---

## 4.6 Bloque 5: Heatmap barrio × año

**Figura**: `07_heatmap_barrio_anio.png`

### Descripción

Heatmap con **índice normalizado (2012 = 100)** para cada barrio y año.

### Hallazgos

**Patrón general**: casi todos los barrios muestran una tendencia
creciente desde 2012, con:
- **Caída en 2020** por COVID.
- **Recuperación fuerte en 2021–2025**.

**Barrios con mayor crecimiento**:
- Barrios periféricos en desarrollo urbanístico.
- Barrios con nueva oferta residencial (Diagonal Mar, Marina del Prat
  Vermell).

**Barrios con mayor estabilidad**:
- Barrios consolidados del centro (Eixample, Gràcia, Sant Gervasi).

**Insight**: la recuperación post-2020 ha sido **desigual**, con los
barrios periféricos y en desarrollo creciendo más rápido que los barrios
consolidados del centro.

---

## 4.7 Bloque 6: Distribución del target

**Figura**: `08_distribucion_target.png`

### Descripción

Dos gráficos:
- **Histograma** de `total_transacciones` con media y mediana.
- **Histograma** de `log(transacciones + 1)`.

### Hallazgos

**Distribución del target**:

| Estadístico | Valor |
|---|---|
| Media | 22,30 |
| Mediana | 16 |
| Std | 23,21 |
| **Skewness** | **2,76** |
| Mín | 0 |
| Máx | 472 |

**Insight**: la distribución es **fuertemente asimétrica a la derecha**.
Esto confirma que necesitaremos transformación log o un modelo Poisson/
Negative Binomial para manejar la varianza.

**El skew de 2,76 es una señal clara** de que el modelo XGBoost con
objetivo `count:poisson` es adecuado para este problema.

---

## 4.8 Análisis descriptivo adicional: SERPAVI vs transacciones

**Figuras**:
- `20_serpavi_vs_transacciones.png`
- `21_serpavi_evolucion.png`

### Descripción

Cruce del **precio medio de alquiler por distrito (SERPAVI 2024)** con
el **volumen de transacciones por distrito (Notariado 2024)**.

### Hallazgos

**Correlaciones**:
- **Pearson**: r = −0,070 (p = 0,848)
- **Spearman**: ρ = −0,273 (p = 0,446)

**Ninguna es estadísticamente significativa**.

**Interpretación**: **NO existe una correlación clara entre el precio
del alquiler y el volumen de transacciones**. Los factores que importan
son:
1. **Tamaño del distrito** (Eixample tiene 6 barrios, Les Corts solo 3).
2. **Stock de vivienda en alquiler** (Eixample 26.768 testigos vs
   Nou Barris 11.991).
3. **Perfil del mercado local** (Ciutat Vella turístico, precio alto y
   pocas transacciones).

**Insight**: si un inversor quiere saber dónde habrá más transacciones,
**NO debe mirar el precio del alquiler**. Debe mirar el tamaño del
distrito, el stock de vivienda y su composición residencial.

---

## 4.9 Análisis descriptivo adicional: extranjeros y vivienda

**Figuras**:
- `22_alquiler_por_distrito.png`
- `23_compraventas_por_distrito.png`
- `24_compradores_extranjeros.png`
- `25_poblacion_extranjera.png`
- `26_inquilinos_extranjeros_estimado.png`

### Descripción

5 gráficos de barras que cruzan:
- **Precio de alquiler** por distrito (SERPAVI 2024).
- **Compraventas** por distrito (Notariado 2024).
- **% de compradores extranjeros** (Ayuntamiento BCN 2025).
- **% de población extranjera** (Padrón 2024).
- **Estimación de % de inquilinos extranjeros** (fórmula).

### Hallazgos clave

**Ciutat Vella es el caso extremo**:
- Alquiler más alto (15,55 €/m²).
- Mayor % compradores extranjeros (42,6%).
- Mayor % población extranjera (63,7%).
- Mayor % inquilinos extranjeros estimado (44,9%).

**Sarrià-Sant Gervasi es el opuesto**:
- Alquiler muy alto (15,38 €/m²).
- Menor % compradores extranjeros (11,5%).
- Menor % población extranjera (15,0%).

**Eixample es el motor del mercado**:
- 4.425 compraventas (el más alto).
- 21,8% inquilinos extranjeros estimado.

**Nou Barris es la paradoja**:
- Alquiler más bajo (12,03 €/m²).
- Pero 28% compradores extranjeros y 32% población extranjera.

### Fórmula de estimación

% inquilinos extranjeros ≈
(% población extranjera) × 70,5%


**Fuente de la tasa del 70,5%**: Institut Metròpoli 2024.

### Limitaciones metodológicas

1. **Datos aproximados**: algunos valores son estimaciones.
2. **Fórmula lineal**: asume tasa de alquiler constante entre distritos.
3. **Padrón cuenta residentes**, no contratos de alquiler.
4. **SERPAVI excluye alquileres** de personas jurídicas.

**Insight**: la población extranjera es **mayoritariamente inquilina**
en Barcelona, especialmente en distritos céntricos y turísticos. Esto
tiene implicaciones para políticas de vivienda y para el mercado de
alquiler.

---

## 4.10 Conclusiones del EDA

### Sobre el mercado

1. **Ciclo completo 2012–2025**: crisis, recuperación, COVID y
   nuevos máximos.
2. **Estacionalidad clara**: julio es el pico, agosto el mínimo.
3. **Concentración espacial**: Eixample y Sant Gervasi concentran la
   mayor actividad.
4. **Tipología dominante**: 67% residencial, 28% aparcamiento.
5. **Distribución asimétrica**: skew 2,76 justifica modelo Poisson.

### Sobre los factores explicativos

6. **El alquiler NO predice transacciones** (correlación nula).
7. **El tamaño del distrito SÍ importa**.
8. **La población extranjera es mayoritariamente inquilina** (70,5%).

### Implicaciones para el modelado

9. **Objetivo Poisson** para XGBoost (varianza > media).
10. **Features clave**: lags, rolling windows, target encoding de
    barrio.
11. **Validación temporal** obligatoria.

---

*Documento generado como parte del Reto 5 — Business Intelligence y Big
Data. Curso Odisea Data, 2025.*