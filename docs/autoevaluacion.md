# Autoevaluación del Reto 5

## Checklist: pasos del reto

- [x] **1. Definición del problema y objetivos**
  - Documento 01: definición clara del business problem, objetivos
    generales y específicos, 5 preguntas de negocio.

- [x] **2. Selección y recolección de datos**
  - Documento 02: fuente principal (Notariado), fuente complementaria
    (SERPAVI), fuente adicional (Padrón).
  - Scripts de ingesta en `src/ingesta/`.

- [x] **3. Preparación y limpieza de datos**
  - Documento 03: pipeline de 5 fases, decisiones metodológicas.
  - Scripts en `src/preparacion/`.
  - Tratamiento de CSV corruptos, valores nulos, outliers.

- [x] **4. Análisis exploratorio (EDA)**
  - Documento 04: 6 bloques temáticos con 8 figuras.
  - Script en `src/analisis/eda_barcelona.py`.

- [x] **5. Desarrollo de modelos analíticos**
  - Documento 05: baseline (Ridge, Lasso) + XGBoost.
  - Machine learning: XGBoost con objetivo Poisson.
  - Scripts en `src/modelado/`.

- [x] **6. Evaluación de modelos**
  - Documento 05: RMSE, MAE, R², MAPE.
  - Análisis de residuos por barrio, mes y magnitud.
  - Detección y corrección de data leakage.

- [x] **7. Recomendaciones y conclusiones**
  - Documento 06: recomendaciones para 4 perfiles de usuario.
  - Limitaciones documentadas.
  - Trabajo futuro en 4 fases.

## Checklist: entregables

- [x] **1. Código y scripts documentados**
  - `src/ingesta/` (2 scripts)
  - `src/preparacion/` (2 scripts)
  - `src/analisis/` (2 scripts)
  - `src/modelado/` (5 scripts)
  - `src/presentacion/` (2 scripts)
  - Código comentado y modular.

- [x] **2. Documentación completa**
  - `reports/documentacion/` (6 documentos)
  - `docs/decisiones_metodologicas.md`
  - `docs/autoevaluacion.md` (este documento)

- [x] **3. Visualizaciones**
  - `reports/figuras/` (26 figuras PNG)
  - `reports/visualizaciones.md` (índice)

- [x] **4. Presentación**
  - `reports/presentacion/presentacion_1_metodologia.pptx` (14 slides)
  - `reports/presentacion/presentacion_2_resultados.pptx` (17 slides)
  - Guiones de audio en el chat

## Puntos fuertes del proyecto

1. **Pipeline completo y reproducible**: desde la descarga de datos hasta
   las conclusiones.
2. **Detección y corrección de data leakage**: hallazgo metodológico
   clave, documentado con transparencia.
3. **Interpretabilidad con SHAP**: 5 visualizaciones diferentes.
4. **Análisis complementario**: SERPAVI + Padrón + extranjeros.
5. **Documentación exhaustiva**: 6 documentos + decisiones metodológicas.
6. **Presentaciones separadas**: metodología (técnica) y resultados
   (negocio), adaptadas a distintas audiencias.
7. **Trabajo futuro estructurado**: 4 fases con acciones concretas.

## Áreas de mejora identificadas

1. **R² limitado a 0,617**: la relación es mayormente lineal; XGBoost no
   aporta mucho sobre Ridge.
2. **Subestimación de picos**: el modelo no captura valores >100.
3. **Correlación SERPAVI nula**: hallazgo honesto pero limitante.
4. **Datos de extranjeros parcialmente estimados**: no hay fuente oficial
   que cruce nacionalidad con distrito.
5. **Un solo ámbito geográfico**: Barcelona. No se ha replicado en otras
   ciudades.

## Valor para el portfolio

- **Proyecto end-to-end** demostrable.
- **Doble perfil**: técnico (código, SHAP) + negocio (recomendaciones).
- **Rigor metodológico**: corrección de leakage, documentación honesta.
- **Reproducibilidad**: todo el pipeline se ejecuta en <1 minuto.

## Conclusión

El proyecto cumple con **los 7 pasos** y **los 4 entregables** del reto.
Además, aporta valor añadido con:
- Análisis descriptivo de extranjeros y vivienda.
- Corrección documentada de data leakage.
- Presentaciones separadas por audiencia.
- Trabajo futuro estructurado.