# 02. Fuentes de datos

## 2.1 Fuente principal: datos.gob.es (Portal Estadístico del Notariado)

Todos los datos del proyecto provienen del **portal de datos abiertos del
Gobierno de España** (`datos.gob.es`), que actúa como agregador de datasets
públicos de distintos organismos oficiales.

El dataset concreto utilizado es:

> **"Número de transmisiones de compraventa de propiedades inmobiliarias
> en la ciudad de Barcelona, según los registros notariales, por tipo de
> uso de la propiedad durante el período especificado."**

### URL de acceso

`https://datos.gob.es`

Búsqueda: "transmisiones inmobiliarias Barcelona notarial".

### Organismo emisor

El dataset lo publica el **Ayuntamiento de Barcelona** a partir de datos
del **Consejo General del Notariado**. `datos.gob.es` actúa como catálogo
agregador.

### Licencia

Datos abiertos publicados bajo licencia compatible con la Ley 37/2007
sobre reutilización de la información del sector público.

## 2.2 Estructura del dataset del Notariado

Se han descargado **15 archivos CSV** correspondientes a los años
**2012–2026**. Cada archivo contiene los datos mensuales de un año
completo.

### Columnas

| Columna | Tipo | Descripción |
|---|---|---|
| `Any` | int | Año |
| `Mes` | int | Mes (1-12) |
| `Codi_Districte` | int | Código del distrito (1-10) |
| `Nom_Districte` | str | Nombre del distrito |
| `Codi_Barri` | int | Código del barrio (1-73) |
| `Nom_Barri` | str | Nombre del barrio |
| `Tipologia_Us_Codi` | int | Código de la tipología de uso |
| `Tipologia_Us_Desc` | str | Descripción de la tipología |
| `num_transacciones` | int | Número de transacciones del mes |

### Tipologías de uso

El campo `Tipologia_Us_Codi` codifica el uso del inmueble transaccionado:

| Código | Descripción |
|---|---|
| 1 | Residencial |
| 2 | Aparcament |
| 3 | Comercial |
| 4 | Oficina |
| 5 | Turístic |
| 8 | Equipaments |
| 9 | No consta |

**Decisión metodológica**: la tipología "No consta" (código 9) se ha
excluido del análisis por tratarse de un cajón de sastre sin valor
interpretativo. Las 6 tipologías restantes se han conservado.

### Cobertura

- **Ámbito territorial**: Barcelona ciudad (73 barrios, 10 distritos).
- **Ámbito temporal**: enero 2012 – diciembre 2025 (excluyendo 2026
  por estar incompleto).
- **Granularidad**: barrio × mes × tipología de uso.

## 2.3 Problemas detectados en la descarga del Notariado

### Formato de los CSV corrupto

Algunos CSV presentaban un formato con **comillas dobles duplicadas**:

"Any,""Mes"",""Codi_Districte"",..."""
"2012,1,1,""Ciutat Vella"",..."""


Esto es habitual cuando se descargan CSV desde navegadores web que
aplican transformaciones automáticas de comillas.

### Solución aplicada

Se desarrolló un **script reparador**
(`src/ingesta/reparar_csv_notariado.py`) que:

1. Lee cada archivo como texto plano.
2. Elimina las comillas exteriores de cada línea.
3. Reemplaza las comillas duplicadas `""` por comillas simples `"`.
4. Guarda el resultado en `data/raw/notariado_limpio/`.

Posteriormente, `src/ingesta/cargar_notariado.py` lee los archivos
reparados **ignorando la cabecera original** y asignando nombres fijos
a las columnas, lo que hace el pipeline robusto ante variaciones del
formato del encabezado.

### Validación posterior

Tras la reparación:
- Los 15 archivos se leen correctamente con `pandas`.
- Los nombres de distrito y barrio tienen los acentos correctos
  (`Gràcia`, `Sagrada Família`, `Sant Martí`).
- Los valores de `num_transacciones` son enteros.

## 2.4 Fuente complementaria: SERPAVI

### Descripción

El **Sistema Estatal de Referencia del Precio del Alquiler de Vivienda
(SERPAVI)** es una base de datos pública del Ministerio de Vivienda y
Agenda Urbana que publica información sobre precios de alquiler en toda
España.

### URL de acceso

`https://www.mivau.gob.es/vivienda/alquila-bien-es-tu-derecho/serpavi`

### Datos descargados

- **Archivo**: Excel completo 2011–2024.
- **Nombre del archivo**: `2026-03-09_bd_SERPAVI_2011-2024 - DEFINITIVO WEB.xlsx`.
- **Ubicación en el proyecto**: `data/raw/serpavi/`.

### Estructura del Excel

El Excel contiene **6 hojas**:

| Hoja | Contenido | Columnas |
|---|---|---|
| 0 | Metadatos | 3 |
| 1 | CCAA | 282 |
| 2 | Provincias | 282 |
| 3 | Municipios | 284 |
| 4 | **Distritos** | **285** |
| 5 | Secciones censales | 285 |

**Para el análisis se ha utilizado la hoja "Distritos"**.

### Formato de la hoja "Distritos"

- **Formato "ancho"**: cada fila es un distrito censal, cada columna
  una variable-año.
- **5 identificadores**:
  - `CPRO`: código de provincia
  - `LITPRO`: nombre de provincia
  - `CUMUN`: código INE de municipio (Barcelona = **08019**)
  - `LITMUN`: nombre del municipio
  - `CUDIS`: código de distrito (ej. `801901` = Ciutat Vella)

- **Variables por año** (patrón `VARIABLE_TIPO_AÑO`):

| Variable | Descripción |
|---|---|
| `BI_ALVHEPCO_TVC_XX` | Número de testigos (vivienda colectiva) |
| `BI_ALVHEPCO_TVU_XX` | Número de testigos (vivienda unifamiliar) |
| `ALQM2_LV_M_VC_XX` | **Alquiler medio €/m²/mes** (vivienda colectiva) |
| `ALQM2_LV_25_VC_XX` | Alquiler percentil 25 €/m²/mes |
| `ALQM2_LV_75_VC_XX` | Alquiler percentil 75 €/m²/mes |
| `ALQTBID12_M_VC_XX` | Alquiler €/mes medio |
| `SLVM2_M_VC_XX` | Superficie media (m²) |

Donde `XX` es el **año abreviado** (`11` = 2011, `24` = 2024).
`VC` = vivienda colectiva; `VU` = vivienda unifamiliar.

### Limitaciones metodológicas

1. **Fuente fiscal, no contractual**: los datos provienen de
   declaraciones fiscales de **personas físicas**, excluyendo
   alquileres de personas jurídicas (sociedades, fondos de inversión).
   Esto significa que **el parque total de alquiler es mayor** que el
   que recoge la fuente.

2. **Mediana del stock, no precio de mercado**: SERPAVI publica la
   mediana del **stock de contratos vigentes**, no precios de nuevos
   contratos. Esto sesga a la baja en zonas donde los precios han
   subido mucho.

3. **Desfase temporal**: los datos se publican con retraso y tienen un
   desfase de hasta 2 años, lo que los hace inservibles para análisis
   contemporáneos.

4. **Críticas del sector**: ASVAL y ACI han señalado que SERPAVI sufre
   "carencias metodológicas como efectos composición, falta de
   diferenciación entre stock y flujos, y heterogeneidad del parque".

### Análisis descriptivo realizado

Se ha cruzado el **alquiler medio 2024 por distrito** (SERPAVI) con el
**volumen de transacciones 2024 por distrito** (Notariado). El script
está en `src/analisis/analisis_serpavi_distrito.py`.

#### Datos cruzados

| Distrito | Alquiler €/m²/mes | Transacciones 2024 |
|---|---|---|
| Ciutat Vella | 15,55 | 1.540 |
| Eixample | 14,27 | **4.425** |
| Sants-Montjuïc | 13,50 | 2.703 |
| Les Corts | 14,91 | **1.196** |
| Sarrià-Sant Gervasi | 15,38 | 2.480 |
| Gràcia | 14,39 | 1.649 |
| Horta-Guinardó | 12,67 | 2.091 |
| Nou Barris | 12,03 | 1.916 |
| Sant Andreu | 12,31 | 1.918 |
| Sant Martí | 13,35 | 3.291 |

#### Correlaciones

| Métrica | Valor | p-value | Interpretación |
|---|---|---|---|
| **Pearson** | **−0,070** | 0,848 | Correlación nula |
| **Spearman** | **−0,273** | 0,446 | Correlación débil negativa |

Ninguna es estadísticamente significativa (p > 0,05).

#### Interpretación

**No existe una correlación estadísticamente significativa entre el
precio del alquiler y el volumen de transacciones a nivel de distrito**
en Barcelona.

Los factores que **sí parecen explicar** el volumen de transacciones son:

1. **Tamaño del distrito**: Eixample (el más grande, 6 barrios) tiene
   4.425 transacciones; Les Corts (3 barrios) tiene 1.196.
2. **Stock de vivienda en alquiler**: Eixample tiene 26.768 testigos;
   Nou Barris solo 11.991.
3. **Perfil del mercado local**: Ciutat Vella tiene el alquiler más
   caro pero pocas transacciones (mercado turístico tensionado).
4. **Desarrollo urbanístico**: Sant Martí (Poblenou, Diagonal Mar)
   tiene alquiler medio pero muchas transacciones (3.291).

**Conclusión de negocio**: si un inversor quiere saber dónde habrá más
transacciones, **NO debe mirar el precio del alquiler**. Debe mirar el
tamaño del distrito, el stock de vivienda y su composición residencial.

#### Limitaciones del análisis

1. **n=10**: muestra muy pequeña, difícil alcanzar significancia.
2. **Sesgo de SERPAVI**: excluye alquileres de personas jurídicas.
3. **Correlación ≠ causalidad**: hay variables de confusión (tamaño,
   población).
4. **Un solo año (2024)**: podría ser atípico.
5. **Nivel distrito**: se pierden dinámicas intra-distrito.

### Trabajo futuro

- **Fase 2**: integrar SERPAVI a nivel de barrio (agregando secciones
  censales) como feature del modelo XGBoost.
- **Fase 3**: calcular la elasticidad del precio de compraventa respecto
  al alquiler (objetivo original del reto).

## 2.5 Fuente complementaria: Idescat (no integrada)

El **Institut d'Estadística de Catalunya (Idescat)** publica datos
demográficos y socioeconómicos a nivel municipal. **No se ha utilizado**
porque:

1. Su granularidad territorial no llega a barrio para los indicadores
   relevantes (población, renta).
2. Requeriría armonización de códigos territoriales.
3. El modelo actual ya alcanza un R² de 0,617 sin estas features.

**Recomendación futura**: integrar Idescat para añadir features
socioeconómicas (población, renta media por barrio) y ver su impacto
en el modelo.

## 2.6 Consideraciones éticas y de privacidad

Los datos utilizados son **estadísticas agregadas** publicadas
oficialmente. **No contienen información personal ni identificable**:

- No permiten identificar personas físicas o jurídicas.
- No contienen precios individuales de operaciones.
- No incluyen características específicas de viviendas concretas.

Su uso está amparado por la legislación vigente sobre datos abiertos
(Ley 37/2007).

## 2.7 Referencias

1. Gobierno de España. *datos.gob.es* — Portal de datos abiertos.
   https://datos.gob.es
2. Consejo General del Notariado. *Portal Estadístico del Notariado*.
   https://www.notariado.org/portal/estadisticas
3. Ministerio de Vivienda y Agenda Urbana. *SERPAVI*.
   https://www.mivau.gob.es/vivienda/alquila-bien-es-tu-derecho/serpavi
4. Institut d'Estadística de Catalunya (fuente complementaria no usada).
   https://www.idescat.cat
5. Ley 37/2007, de 16 de noviembre, sobre reutilización de la información
   del sector público.

---

*Documento generado como parte del Reto 5 — Business Intelligence y Big
Data. Curso Odisea Data, 2025.*