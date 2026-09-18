# Predicción de Precios de Vivienda en Cataluña
## Reto 5 · Business Intelligence y Big Data · Curso 6

### Objetivo
Modelo predictivo del precio de compraventa (€/m²) a nivel municipal
en Cataluña, con interpretabilidad vía SHAP.

### Preguntas de negocio
- Q1: ¿La elasticidad del precio de compraventa respecto al alquiler
      es distinta por comarca?
- Q2: ¿La obra nueva es indicador adelantado o retardado del precio?
- Q3: ¿Qué municipios mantienen prima/descuento tras controlar
      alquiler y oferta?

### Fuentes de datos
- Idescat / Registradores: compraventas (target)
- SERPAVI: precio de alquiler
- HABIT: obra nueva (iniciadas/acabadas)
- Idescat: población municipal

### Stack
Python · pandas · scikit-learn · XGBoost · SHAP · geopandas

### Estructura del proyecto

data/raw/ → datos originales sin modificar
data/interim/ → merges parciales
data/processed/ → dataset final para modelar
notebooks/ → exploración
src/ → código de producción
models/ → modelos entrenados
reports/ → entregables del reto