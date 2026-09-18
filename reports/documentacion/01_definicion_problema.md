# 01. Definición del problema y objetivos

## 1.1 Contexto de negocio

El mercado inmobiliario de Barcelona es uno de los más dinámicos y volátiles
de Europa. La ciudad ha experimentado en los últimos 15 años:

- Una **crisis inmobiliaria severa** (2008–2013) con caída de precios y
  transacciones.
- Una **recuperación sostenida** (2014–2019).
- Una **caída puntual por COVID-19** (2020).
- Una **fase de reactivación y máximos históricos** (2021–2025).

En este contexto, **anticipar el volumen de transacciones inmobiliarias**
por barrio es crítico para múltiples actores:

- **Inversores inmobiliarios**: identifican barrios con actividad creciente
  antes de que los precios suban.
- **Agencias inmobiliarias**: planifican recursos y priorizan zonas.
- **Administraciones públicas**: monitorizan dinámicas de gentrificación
  o desplazamiento residencial.
- **Entidades financieras**: ajustan su exposición al riesgo hipotecario
  por zonas.

## 1.2 Problema de negocio

**No existe un modelo público y reproducible que prediga el número de
transacciones inmobiliarias a nivel de barrio en Barcelona**, ni que
identifique qué factores (tendencia histórica, alquiler, tipología de uso,
estacionalidad) las explican.

## 1.3 Objetivos del proyecto

### Objetivo general

Diseñar y ejecutar un proyecto completo de Business Analytics que permita
**predecir el número de transacciones inmobiliarias mensuales por barrio
en Barcelona** y **explicar los factores que las determinan**.

### Objetivos específicos

1. **Construir un dataset consolidado** a partir de fuentes oficiales
   (Portal Estadístico del Notariado, Idescat, SERPAVI).
2. **Analizar patrones temporales y espaciales** del mercado inmobiliario
   de Barcelona (2012–2025).
3. **Comparar modelos predictivos**: baseline lineal (Ridge, Lasso) vs.
   modelo avanzado (XGBoost).
4. **Interpretar el modelo final con SHAP** para identificar las variables
   más influyentes y su relación con la predicción.
5. **Generar recomendaciones accionables** para los distintos actores
   del mercado inmobiliario.

## 1.4 Preguntas de negocio

El proyecto responde a las siguientes preguntas:

### Pregunta 1 — Tendencia temporal
**¿Cómo ha evolucionado el volumen de transacciones en Barcelona entre
2012 y 2025? ¿Qué impacto tuvo el COVID-19 y la recuperación posterior?**

### Pregunta 2 — Estacionalidad
**¿Existe un patrón estacional claro en las transacciones? ¿Qué meses
concentran mayor y menor actividad?**

### Pregunta 3 — Heterogeneidad espacial
**¿Qué barrios concentran la mayor actividad inmobiliaria? ¿Qué barrios
muestran patrones atípicos (muy alta o muy baja actividad)?**

### Pregunta 4 — Factores determinantes
**¿Qué variables explican mejor el número de transacciones de un barrio
en un mes concreto? ¿Es la tendencia histórica más importante que la
estacionalidad o el tipo de uso?**

### Pregunta 5 — Predicción
**¿Podemos predecir con precisión el número de transacciones del mes
siguiente por barrio? ¿Qué modelos funcionan mejor y con qué limitaciones?**

## 1.5 Alcance del proyecto

### Incluido en el alcance

- **Ámbito territorial**: Barcelona ciudad (68 barrios tras filtrado).
- **Ámbito temporal**: enero 2012 – diciembre 2025 (14 años, 167 meses).
- **Tipologías de uso**: Residencial, Aparcamiento, Comercial, Oficina,
  Turístico, Equipamientos.
- **Modelado**: predicción del número de transacciones totales mensuales
  por barrio.

### Fuera del alcance

- **Precio de compraventa** (€/m²): no incluido en el dataset principal.
  Sugerencia: ampliar con datos del SERPAVI o del Colegio de Registradores
  en futuras iteraciones.
- **Análisis causal**: SHAP mide **asociación**, no causalidad. No podemos
  afirmar que "X causa Y" solo porque SHAP lo señale como relevante.
- **Predicción de precios**: el proyecto se centra en **volumen de
  transacciones**, no en precios.
- **Expansión a otras ciudades**: se ha elegido Barcelona por disponibilidad
  de datos granulares. Madrid y otras ciudades requerirían fuentes
  adicionales.

## 1.6 Metodología

Se sigue un **pipeline clásico de Business Analytics** alineado con las
mejores prácticas de la industria:

1. **Definición del problema** (este documento).
2. **Identificación y recolección de datos**.
3. **Preparación y limpieza**.
4. **Análisis exploratorio (EDA)**.
5. **Feature engineering**.
6. **Modelado** (baseline + XGBoost).
7. **Evaluación** (métricas + residuos).
8. **Interpretabilidad** (SHAP).
9. **Recomendaciones y conclusiones**.

Cada fase está documentada en un archivo independiente dentro de este
directorio.

## 1.7 Entregables

Los entregables del proyecto son:

1. **Código completo** (`src/`) documentado y reproducible.
2. **Documentación detallada** (este directorio).
3. **Visualizaciones** (`reports/figuras/`) de resultados clave.
4. **Presentación ejecutiva** (`reports/presentacion/`) con los hallazgos
   principales.

## 1.8 Métricas de éxito

El proyecto se considera exitoso si:

- El modelo final supera al baseline en **RMSE y R²**.
- El R² del modelo en test es **≥ 0,60** (buena capacidad explicativa).
- Se obtiene una **interpretación clara** de las features más influyentes
  vía SHAP.
- Se generan **al menos 5 recomendaciones accionables** basadas en los
  resultados.

---

*Documento generado como parte del Reto 5 — Business Intelligence y Big
Data. Curso Odisea Data, 2025.*