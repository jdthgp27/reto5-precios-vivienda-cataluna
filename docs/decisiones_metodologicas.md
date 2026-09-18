# Decisiones metodológicas

## 1. Ámbito territorial y temporal

- **Ámbito**: Barcelona ciudad (73 barrios, 10 distritos)
- **Periodo**: enero 2012 – diciembre 2025 (14 años completos)
- **Excluido 2026**: año incompleto en el momento de la descarga (solo enero-febrero)

## 2. Filtrado de barrios

- **Criterio aplicado**: excluir barrios con >90% de meses sin actividad
- **Barrios excluidos**:
  - Can Peguera (100% ceros)
  - Vallbona (100% ceros)
  - Torre Baró (97,6% ceros)
  - Baró de Viver (97,0% ceros)
  - la Clota (92,9% ceros)
- **Justificación**: estos 5 barrios aportan menos del 1% de las transacciones totales y añaden ruido al modelo (predicen 0 casi siempre).
- **Resultado**: 68 barrios para el análisis

## 3. Tratamiento de tipologías

- **Mantenidas**: Residencial, Aparcament, Comercial, Oficina, Turístic, Equipaments
- **Excluida**: "No consta" (ruido, sin valor informativo sobre el uso real)
- **Target del modelo**: `num_transacciones` (total agregado por barrio-mes)

## 4. Pendiente de documentar

- Filtros en modelado (lags, outliers)
- Estrategia de validación (split temporal)
- Métricas elegidas y justificación