# 06. Conclusiones y recomendaciones

## 6.1 Resumen ejecutivo

Este proyecto ha construido un **modelo predictivo del número de
transacciones inmobiliarias mensuales por barrio en Barcelona**, con
datos del Portal Estadístico del Notariado (2012–2025) y análisis
complementario de SERPAVI.

### Resultados clave

| Aspecto | Resultado |
|---|---|
| **Modelo final** | XGBoost con objetivo Poisson |
| **R² en test** | 0,617 |
| **RMSE en test** | 15,77 transacciones |
| **MAE en test** | 9,26 transacciones |
| **MAPE** | 36,7% |
| **Dataset** | 68 barrios × 167 meses |
| **Transacciones analizadas** | 254.732 |

### Hallazgos principales

1. **El mercado inmobiliario de Barcelona ha pasado por un ciclo
   completo** en 14 años: crisis (2012), recuperación (2014–2019),
   COVID (2020) y máximos históricos (2025).

2. **La tendencia histórica del barrio es el factor más predictivo**
   (`rolling_12m` con 23,7% del impacto SHAP).

3. **La identidad del barrio es clave** (`barrio_te` con 13,3% del
   impacto): cada barrio tiene un patrón propio.

4. **Julio es el mes de mayor actividad y agosto el menor**, aunque el
   pico se debe al retraso de las escrituras notariales.

5. **El precio del alquiler NO predice el volumen de transacciones**
   (correlación nula, r=−0,07).

6. **La población extranjera es mayoritariamente inquilina** (70,5%),
   especialmente en distritos céntricos como Ciutat Vella.

7. **El modelo funciona bien en valores típicos (15–60 transacciones)**
   pero subestima sistemáticamente los picos (>100).

---

## 6.2 Recomendaciones por perfil de usuario

### 6.2.1 Inversores inmobiliarios

**Contexto**: quieren identificar oportunidades de inversión antes de
que los precios suban.

**Recomendaciones**:

1. **Mirar el tamaño del distrito, NO el precio del alquiler**. El
   análisis SERPAVI vs transacciones muestra que no hay correlación
   entre alquiler y volumen. Los factores que importan son:
   - Número de barrios del distrito.
   - Stock de vivienda en alquiler (testigos SERPAVI).
   - Composición residencial vs turística.

2. **Priorizar barrios con alto `rolling_12m`**: son los que tienen
   tendencia sostenida de actividad. Ejemplos: Eixample, Sant Martí,
   Sant Gervasi.

3. **Vigilar barrios emergentes con `rolling_12m` bajo pero picos
   recientes**: Marina del Prat Vermell (julio 2025 con 296
   transacciones), Diagonal Mar, Poblenou. Son zonas en desarrollo
   urbanístico.

4. **Evitar barrios con >80% de meses sin actividad**: Can Peguera,
   Vallbona, Torre Baró. El mercado es demasiado ilíquido.

### 6.2.2 Agencias inmobiliarias

**Contexto**: quieren planificar recursos y priorizar zonas.

**Recomendaciones**:

1. **Concentrar esfuerzo comercial en el Top 10 de barrios**: Sant
   Gervasi - Galvany, Nova Esquerra de l'Eixample, Dreta de l'Eixample,
   Sant Andreu, la Sagrada Família, les Corts, Gràcia, el Raval,
   Antiga Esquerra, el Poblenou. Representan el **~35% del mercado**.

2. **Planificar por estacionalidad**:
   - **Julio**: pico máximo de actividad. Reforzar equipo comercial.
   - **Agosto**: valle profundo. Reducir costes operativos.
   - **Marzo–junio**: temporada alta estable. Mantener plantilla.

3. **Adaptar la oferta al perfil del barrio**:
   - **Ciutat Vella**: 42,6% de compradores extranjeros. Ofrecer
     servicios en inglés, francés, italiano.
   - **Sarrià-Sant Gervasi**: 11,5% de compradores extranjeros. Enfoque
     en cliente local de alto poder adquisitivo.

4. **Usar el modelo para prever demanda mensual**: el modelo XGBoost
   predice con R²=0,617 el volumen de transacciones del próximo mes
   por barrio. Útil para ajustar cartera de propiedades.

### 6.2.3 Administraciones públicas

**Contexto**: quieren monitorizar dinámicas de gentrificación y
desplazamiento.

**Recomendaciones**:

1. **Vigilar la presión de alquiler en Ciutat Vella**:
   - 63,7% de población extranjera.
   - 44,9% de inquilinos extranjeros estimados.
   - Alquiler más alto de la ciudad (15,55 €/m²).
   - **Riesgo**: desplazamiento de población local.

2. **Monitorizar barrios emergentes**:
   - Marina del Prat Vermell: picos de 296 transacciones en julio
     2025 (frente a una media de 4,7). Es un barrio en pleno
     desarrollo urbanístico.
   - Diagonal Mar: 472 transacciones en mayo 2014. Zona de nueva
     construcción con operaciones concentradas.

3. **Planificar vivienda protegida en distritos con alta presión**:
   - Ciutat Vella.
   - Eixample (mayor volumen absoluto: 4.425 transacciones en 2024).
   - Sant Martí (3.291 transacciones).

4. **Usar el modelo para anticipar tensiones**:
   - Barrios con `rolling_12m` creciente y `pct_turistico` creciente
     son candidatos a gentrificación.
   - Monitorizar trimestralmente.

### 6.2.4 Entidades financieras

**Contexto**: quieren ajustar exposición al riesgo hipotecario por
zonas.

**Recomendaciones**:

1. **Ajustar el scoring por barrio**:
   - Barrios con alta volatilidad (la Vila Olímpica del Poblenou,
     Marina del Prat Vermell) → mayor prima de riesgo.
   - Barrios estables (el Poble Sec, el Clot, Hostafrancs) → menor
     prima.

2. **Anticipar picos de demanda hipotecaria**:
   - El modelo predice el volumen mensual de transacciones.
   - Julio y otoño son los meses de mayor demanda.
   - Reforzar equipos de análisis en esas fechas.

3. **Segmentar por perfil de comprador**:
   - **Ciutat Vella**: 42,6% extranjeros → productos específicos
     (hipotecas para no residentes, multi-divisa).
   - **Sarrià-Sant Gervasi**: 11,5% extranjeros → enfoque en cliente
     local premium.

4. **Evitar exposición excesiva en barrios con >80% de meses sin
   actividad** (Can Peguera, Vallbona, Torre Baró).

---

## 6.3 Limitaciones metodológicas

### Del dataset

1. **Granularidad temporal mensual**: no permite detectar dinámicas
   intra-mensuales.
2. **Granularidad espacial por barrio**: se pierden dinámicas
   intra-barrio.
3. **Datos del Notariado con retraso**: 2–3 meses de desfase respecto
   a la operación real.
4. **Cobertura limitada**: solo barrios con >2 transacciones en el
   período se publican.
5. **Falta de precio €/m²**: el dataset no incluye precios de
   compraventa.

### Del modelo

1. **Subestima valores altos**: el MAE en el rango 100+ es 67,5.
2. **Sobreestima valores bajos**: en el rango 0-5 sobreestima por 8,56.
3. **Residuos sesgados**: skewness 4,22, kurtosis 52,04.
4. **No captura picos extremos**: el caso de Marina del Prat Vermell
   en julio 2025 (real=296, pred=15,5) es un ejemplo.
5. **R² limitado a 0,617**: hay margen de mejora.

### Del análisis complementario

1. **SERPAVI sesgado**: excluye alquileres de personas jurídicas
   (sociedades, fondos).
2. **Correlación ≠ causalidad**: SHAP mide asociación, no causa.
3. **Datos de extranjeros aproximados**: parte de los valores por
   distrito son estimaciones.
4. **Fórmula lineal simplificada**: asume tasa de alquiler constante
   entre distritos.

### Del proyecto

1. **n=10 distritos**: muestra pequeña para análisis estadísticos
   robustos.
2. **Un solo ámbito geográfico**: Barcelona. No extrapolable a otras
   ciudades sin reentrenar.
3. **Período 2012–2025**: incluye una crisis y una pandemia, lo que
   puede sesgar el modelo.

---

## 6.4 Trabajo futuro

### Fase 2: Integración de Idescat

**Objetivo**: añadir features socioeconómicas al modelo.

**Acciones**:
1. Descargar datos de población por barrio (Padrón municipal continuo).
2. Descargar datos de renta media por barrio (Agencia Tributaria +
   Idescat).
3. Armonizar códigos territoriales (barrio notarial vs barrio
   estadístico).
4. Reentrenar XGBoost con estas features.
5. Medir la mejora en R² y RMSE.

**Impacto esperado**: R² de 0,617 → 0,70+.

### Fase 3: Integración de SERPAVI a nivel de barrio

**Objetivo**: incorporar el alquiler como feature del modelo.

**Acciones**:
1. Descargar SERPAVI a nivel de sección censal.
2. Agregar secciones censales a barrios.
3. Calcular la mediana de alquiler por barrio y año.
4. Añadir como feature al modelo.
5. Calcular la **elasticidad del precio de compraventa respecto al
   alquiler** (objetivo original del reto).

**Impacto esperado**: responder la pregunta original del reto sobre
cómo varía la elasticidad por distrito.

### Fase 4: Modelo hurdle (zero-inflated)

**Objetivo**: mejorar la predicción de valores extremos.

**Acciones**:
1. Separar el problema en dos:
   - **Clasificador**: ¿habrá transacciones? (0 vs >0)
   - **Regresor**: ¿cuántas? (condicional a >0)
2. Entrenar dos modelos independientes.
3. Combinar las predicciones.

**Impacto esperado**: mejor manejo de los ceros y de los picos.

### Fase 5: Expansión a otras ciudades

**Objetivo**: replicar el análisis en Madrid, Valencia, Sevilla.

**Acciones**:
1. Buscar datasets equivalentes en `datos.gob.es` para cada ciudad.
2. Adaptar el pipeline (armonización de códigos territoriales).
3. Entrenar modelos específicos por ciudad.
4. Comparar patrones entre ciudades.

---

## 6.5 Valor aportado por el proyecto

### Valor técnico

1. **Pipeline reproducible** de ingesta, limpieza, feature engineering
   y modelado.
2. **Detección y corrección de data leakage**, con documentación
   metodológica.
3. **Modelo interpretable** con SHAP, que permite entender qué
   factores influyen en las transacciones.
4. **Análisis de residuos profundo**, que identifica las limitaciones
   del modelo.

### Valor de negocio

1. **Predicción mensual** del volumen de transacciones por barrio.
2. **Identificación de barrios emergentes** (Marina del Prat Vermell,
   Diagonal Mar).
3. **Análisis de la población extranjera** y su impacto en el mercado
   de alquiler.
4. **Recomendaciones accionables** para 4 perfiles de usuario.

### Valor metodológico

1. **Documentación exhaustiva** de todas las decisiones.
2. **Corrección de un error grave** (data leakage) con transparencia.
3. **Análisis honesto de limitaciones** (subestimación de valores
   altos, residuos sesgados).
4. **Propuesta de trabajo futuro** estructurada en 4 fases.

### Valor para el portfolio

1. **Proyecto end-to-end**: desde la ingesta hasta las conclusiones.
2. **Código modular y documentado** (`src/`).
3. **Visualizaciones profesionales** (21 figuras).
4. **Presentación ejecutiva** con hallazgos clave.

---

## 6.6 Reflexión final

Este proyecto demuestra que **Business Analytics no es solo aplicar
modelos**, sino:

1. **Entender el problema de negocio** antes de tocar datos.
2. **Documentar cada decisión metodológica** (filtros, correcciones,
   supuestos).
3. **Detectar errores** (data leakage) y corregirlos con transparencia.
4. **Interpretar los resultados** con SHAP para generar insights
   accionables.
5. **Reconocer las limitaciones** del modelo y proponer mejoras.

El modelo final tiene un **R² de 0,617**, que es un resultado
razonable para un problema de predicción de transacciones inmobiliarias
con datos agregados. **No es un modelo perfecto**, pero es un modelo
**honesto, interpretable y útil** para la toma de decisiones.

---

*Documento generado como parte del Reto 5 — Business Intelligence y Big
Data. Curso Odisea Data, 2025.*