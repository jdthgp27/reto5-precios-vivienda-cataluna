# generar_presentacion_metodologia.py
# Genera la presentacion PPTX de metodologia del proyecto.
#
# Uso:
#   python src/presentacion/generar_presentacion_metodologia.py
#
# Salida:
#   reports/presentacion/presentacion_1_metodologia.pptx

from pathlib import Path
import sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.utilidades.config import BASE_DIR, FIGURAS_DIR


SALIDA_PPTX = BASE_DIR / "reports" / "presentacion" / "presentacion_1_metodologia.pptx"

# ============================================================
# DISENO
# ============================================================
COLOR_PRIMARIO = RGBColor(0x2E, 0x86, 0xAB)      # azul corporativo
COLOR_ACENTO = RGBColor(0xF1, 0x8F, 0x01)         # naranja
COLOR_FONDO = RGBColor(0xF5, 0xF7, 0xFA)          # gris muy claro
COLOR_TEXTO = RGBColor(0x2C, 0x3E, 0x50)          # gris oscuro
COLOR_GRIS_CLARO = RGBColor(0xBD, 0xC3, 0xC7)
COLOR_BLANCO = RGBColor(0xFF, 0xFF, 0xFF)

FUENTE_TITULO = "Calibri"
FUENTE_TEXTO = "Calibri"


# ============================================================
# UTILIDADES
# ============================================================
def nuevo_slide(prs):
    """Anade un slide en blanco."""
    return prs.slides.add_slide(prs.slide_layouts[6])


def anadir_barra_lateral(slide, prs):
    """Anade una barra de color a la izquierda."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.25), prs.slide_height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = COLOR_PRIMARIO
    shape.line.fill.background()


def anadir_titulo(slide, texto, color=COLOR_PRIMARIO, tamano=28):
    """Anade un titulo al slide."""
    txBox = slide.shapes.add_textbox(Inches(0.7), Inches(0.4),
                                       Inches(12), Inches(0.9))
    tf = txBox.text_frame
    tf.text = texto
    p = tf.paragraphs[0]
    p.font.name = FUENTE_TITULO
    p.font.size = Pt(tamano)
    p.font.bold = True
    p.font.color.rgb = color


def anadir_subtitulo(slide, texto, tamano=16):
    """Anade un subtitulo."""
    txBox = slide.shapes.add_textbox(Inches(0.7), Inches(1.3),
                                       Inches(12), Inches(0.6))
    tf = txBox.text_frame
    tf.text = texto
    p = tf.paragraphs[0]
    p.font.name = FUENTE_TEXTO
    p.font.size = Pt(tamano)
    p.font.italic = True
    p.font.color.rgb = COLOR_TEXTO


def anadir_bullets(slide, items, left=0.7, top=2.0, width=12, height=5.5,
                    tamano=14):
    """Anade una lista con bullets."""
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top),
                                       Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True

    for i, item in enumerate(items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()

        # Detectar nivel (indentacion)
        nivel = 0
        if item.startswith("  - "):
            nivel = 1
            item = item[4:]
        elif item.startswith("    - "):
            nivel = 2
            item = item[6:]
        elif item.startswith("- "):
            item = item[2:]

        p.text = ("• " if nivel == 0 else "  ◦ ") + item
        p.font.name = FUENTE_TEXTO
        p.font.size = Pt(tamano if nivel == 0 else tamano - 2)
        p.font.color.rgb = COLOR_TEXTO
        p.space_after = Pt(6)
        p.level = nivel


def anadir_imagen_centrada(slide, ruta_img, top=2.0, height=4.5):
    """Anade una imagen centrada horizontalmente."""
    if not Path(ruta_img).exists():
        print(f"  AVISO: no existe {ruta_img}")
        return
    slide.shapes.add_picture(
        str(ruta_img),
        left=Inches(1.5), top=Inches(top),
        height=Inches(height),
    )


def anadir_caja_destacada(slide, texto, top=2.0, left=1.0, width=11, height=1.2,
                            color_fondo=COLOR_PRIMARIO):
    """Anade una caja con texto destacado."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color_fondo
    shape.line.fill.background()

    tf = shape.text_frame
    tf.word_wrap = True
    tf.text = texto
    p = tf.paragraphs[0]
    p.font.name = FUENTE_TEXTO
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLANCO
    p.alignment = PP_ALIGN.CENTER


def fondo_claro(slide, prs):
    """Pone fondo claro al slide."""
    fondo = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    fondo.fill.solid()
    fondo.fill.fore_color.rgb = COLOR_FONDO
    fondo.line.fill.background()
    # Mover al fondo
    spTree = fondo._element.getparent()
    spTree.remove(fondo._element)
    spTree.insert(2, fondo._element)


# ============================================================
# SLIDES
# ============================================================
def slide_01_portada(prs):
    slide = nuevo_slide(prs)
    anadir_barra_lateral(slide, prs)

    # Bloque grande de color
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.25), 0,
        prs.slide_width - Inches(0.25), Inches(3.5)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = COLOR_PRIMARIO
    shape.line.fill.background()

    # Titulo principal
    txBox = slide.shapes.add_textbox(Inches(1), Inches(0.8),
                                       Inches(11), Inches(1.2))
    tf = txBox.text_frame
    tf.text = "Predicción de Transacciones Inmobiliarias"
    p = tf.paragraphs[0]
    p.font.name = FUENTE_TITULO
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLANCO

    # Subtitulo
    txBox2 = slide.shapes.add_textbox(Inches(1), Inches(2.0),
                                        Inches(11), Inches(0.8))
    tf2 = txBox2.text_frame
    tf2.text = "Barcelona 2012-2025 · Metodología del proyecto"
    p2 = tf2.paragraphs[0]
    p2.font.name = FUENTE_TEXTO
    p2.font.size = Pt(20)
    p2.font.color.rgb = COLOR_BLANCO

    # Pie
    txBox3 = slide.shapes.add_textbox(Inches(1), Inches(4.5),
                                        Inches(11), Inches(2))
    tf3 = txBox3.text_frame
    tf3.text = "Reto 5 · Business Intelligence y Big Data"
    p3 = tf3.paragraphs[0]
    p3.font.size = Pt(18)
    p3.font.bold = True
    p3.font.color.rgb = COLOR_TEXTO

    p4 = tf3.add_paragraph()
    p4.text = "Curso Odisea Data · 2025"
    p4.font.size = Pt(14)
    p4.font.color.rgb = COLOR_TEXTO


def slide_02_indice(prs):
    slide = nuevo_slide(prs)
    anadir_barra_lateral(slide, prs)
    anadir_titulo(slide, "Índice de la presentación")

    items = [
        "1. El reto y su contexto",
        "2. Preguntas de negocio",
        "3. Fuentes de datos",
        "4. Pipeline del proyecto (5 fases)",
        "5. Fase 1: Reparación de CSV",
        "6. Fase 2: Ingesta y agregación",
        "7. Fase 3: Filtrado de barrios y meses",
        "8. Fase 4: Feature engineering",
        "9. Fase 5: Split temporal",
        "10. Detección y corrección de data leakage",
        "11. Modelado: Ridge vs XGBoost",
        "12. Validación temporal",
    ]
    anadir_bullets(slide, items, top=1.8, tamano=15)


def slide_03_reto(prs):
    slide = nuevo_slide(prs)
    anadir_barra_lateral(slide, prs)
    anadir_titulo(slide, "1. El reto y su contexto")
    anadir_subtitulo(slide, "Business problem")

    anadir_caja_destacada(
        slide,
        "Predecir el número de transacciones inmobiliarias\n"
        "mensuales por barrio en Barcelona",
        top=2.0, height=1.4,
    )

    items = [
        "Contexto de negocio",
        "  - Mercado inmobiliario volátil (crisis 2012, COVID 2020, máximos 2025)",
        "  - Falta de modelos públicos y reproducibles a nivel de barrio",
        "  - Actores afectados: inversores, agencias, administraciones, banca",
        "",
        "Objetivo general",
        "  - Diseñar un proyecto completo de Business Analytics",
        "  - Combinar metodologías y mejores prácticas de la industria",
        "  - Generar insights accionables para la toma de decisiones",
    ]
    anadir_bullets(slide, items, top=3.7, tamano=13)


def slide_04_preguntas(prs):
    slide = nuevo_slide(prs)
    anadir_barra_lateral(slide, prs)
    anadir_titulo(slide, "2. Preguntas de negocio")

    items = [
        "P1: ¿Cómo ha evolucionado el volumen de transacciones en Barcelona (2012-2025)?",
        "P2: ¿Existe un patrón estacional claro? ¿Qué meses concentran más actividad?",
        "P3: ¿Qué barrios concentran la mayor actividad inmobiliaria?",
        "P4: ¿Qué variables explican mejor el número de transacciones de un barrio?",
        "P5: ¿Podemos predecir con precisión el número de transacciones del mes siguiente?",
        "",
        "Objetivos específicos:",
        "  - Construir un dataset consolidado desde fuentes oficiales",
        "  - Analizar patrones temporales y espaciales",
        "  - Comparar baseline vs modelo avanzado",
        "  - Interpretar el modelo con SHAP",
        "  - Generar recomendaciones accionables",
    ]
    anadir_bullets(slide, items, top=1.8, tamano=13)


def slide_05_fuentes(prs):
    slide = nuevo_slide(prs)
    anadir_barra_lateral(slide, prs)
    anadir_titulo(slide, "3. Fuentes de datos")

    items = [
        "Fuente principal: datos.gob.es (Portal Estadístico del Notariado)",
        "  - 15 archivos CSV · 2012-2026",
        "  - Granularidad: barrio × mes × tipología de uso",
        "  - 36.771 filas tras consolidación",
        "  - Organismo emisor: Consejo General del Notariado",
        "",
        "Fuente complementaria: SERPAVI",
        "  - Excel con datos 2011-2024",
        "  - Granularidad: sección censal, distrito, municipio",
        "  - Precio medio alquiler €/m²/mes",
        "  - Organismo emisor: Ministerio de Vivienda",
        "",
        "Fuente complementaria: Padrón Municipal 2024",
        "  - Población extranjera por distrito",
        "  - Uso: análisis descriptivo adicional",
    ]
    anadir_bullets(slide, items, top=1.8, tamano=12)


def slide_06_pipeline(prs):
    slide = nuevo_slide(prs)
    anadir_barra_lateral(slide, prs)
    anadir_titulo(slide, "4. Pipeline del proyecto")

    # Cajas del pipeline
    cajas = [
        ("1. Reparación\nCSV", 0.8, 2.3),
        ("2. Ingesta\ny consolidación", 3.3, 2.3),
        ("3. Agregación\nbarrio-mes", 5.8, 2.3),
        ("4. Filtrado\ny limpieza", 8.3, 2.3),
        ("5. Feature\nengineering", 10.8, 2.3),
    ]

    for texto, left, top in cajas:
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(left), Inches(top), Inches(2.0), Inches(1.5)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = COLOR_PRIMARIO
        shape.line.fill.background()

        tf = shape.text_frame
        tf.word_wrap = True
        tf.text = texto
        p = tf.paragraphs[0]
        p.font.name = FUENTE_TEXTO
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = COLOR_BLANCO
        p.alignment = PP_ALIGN.CENTER

    # Flechas (triangulos)
    for left in [2.85, 5.35, 7.85, 10.35]:
        shape = slide.shapes.add_shape(
            MSO_SHAPE.RIGHT_ARROW,
            Inches(left), Inches(2.85), Inches(0.4), Inches(0.4)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = COLOR_ACENTO
        shape.line.fill.background()

    # Descripcion debajo
    items = [
        "Cada fase está implementada en un script independiente y reproducible.",
        "Todo el pipeline se ejecuta en menos de 1 minuto.",
        "Fuente: 15 archivos CSV originales → 1 dataset consolidado.",
    ]
    anadir_bullets(slide, items, top=4.5, tamano=14)


def slide_07_fase1(prs):
    slide = nuevo_slide(prs)
    anadir_barra_lateral(slide, prs)
    anadir_titulo(slide, "5. Fase 1: Reparación de CSV")

    items = [
        "Problema detectado",
        "  - Los CSV descargados tienen comillas dobles duplicadas",
        '  - Ejemplo: "Any,""Mes"",""Codi_Districte""..."',
        "  - Esto rompe pandas al leerlos",
        "",
        "Solución implementada (reparar_csv_notariado.py)",
        "  - Leer los archivos como texto plano",
        "  - Eliminar comillas exteriores y duplicadas",
        "  - Guardar en data/raw/notariado_limpio/",
        "",
        "Resultado",
        "  - 15 archivos reparados correctamente",
        "  - Acentos y caracteres especiales OK (Gràcia, Sagrada Família)",
        "  - Lectura con pandas sin errores",
    ]
    anadir_bullets(slide, items, top=1.8, tamano=13)


def slide_08_fase2(prs):
    slide = nuevo_slide(prs)
    anadir_barra_lateral(slide, prs)
    anadir_titulo(slide, "6. Fase 2: Ingesta y agregación")

    items = [
        "Ingesta (cargar_notariado.py)",
        "  - Leer los 15 CSV ignorando la cabecera original",
        "  - Asignar nombres fijos de columna (más robusto)",
        "  - Consolidar en data/interim/notariado_barcelona.csv",
        "  - 36.771 filas",
        "",
        "Agregación (agregar_notariado_barcelona.py)",
        "  - Vista 1: barrio × mes (total de transacciones)",
        "  - Vista 2: barrio × mes × tipología",
        "  - Relleno de meses faltantes con 0",
        "",
        "Decisión metodológica",
        "  - Excluir tipología 'No consta' (cajón de sastre sin valor)",
        "  - 6 tipologías finales: Residencial, Aparcament, Comercial,",
        "    Oficina, Turístic, Equipaments",
    ]
    anadir_bullets(slide, items, top=1.8, tamano=12)


def slide_09_fase3(prs):
    slide = nuevo_slide(prs)
    anadir_barra_lateral(slide, prs)
    anadir_titulo(slide, "7. Fase 3: Filtrado")

    items = [
        "Filtro 1: Barrios con >90% de meses sin transacciones",
        "  - 5 barrios excluidos: Can Peguera, Vallbona, Torre Baró,",
        "    Baró de Viver, la Clota",
        "  - Aportan menos del 1% de las transacciones totales",
        "",
        "Filtro 2: Meses corruptos",
        "  - Agosto 2013: solo 15 transacciones en toda Barcelona",
        "    (vs ~500 de media histórica del mismo mes)",
        "  - Datos claramente incompletos en la fuente original",
        "",
        "Meses revisados pero NO eliminados",
        "  - 2012-2013: valores bajos coherentes con la crisis inmobiliaria",
        "  - Octubre 2023: 90% caída (no 97% como agosto 2013),",
        "    coincide con incertidumbre política y subida de tipos",
        "",
        "Resultado final: 68 barrios × 167 meses = 11.356 filas",
    ]
    anadir_bullets(slide, items, top=1.8, tamano=12)


def slide_10_fase4(prs):
    slide = nuevo_slide(prs)
    anadir_barra_lateral(slide, prs)
    anadir_titulo(slide, "8. Fase 4: Feature engineering")

    items = [
        "Features temporales (5)",
        "  - mes_sin, mes_cos (codificación cíclica del mes)",
        "  - trimestre, tendencia, es_agosto",
        "",
        "Lags (5)",
        "  - lag_1, lag_2, lag_3 (meses anteriores)",
        "  - lag_12 (mismo mes del año anterior)",
        "  - diff_1 (diferencia entre lag_1 y lag_2)",
        "",
        "Rolling windows (3)",
        "  - rolling_3m, rolling_6m, rolling_12m (medias móviles)",
        "",
        "Tipologías (6) - con lag 1 para evitar leakage",
        "  - pct_residencial, pct_aparcament, pct_comercial, ...",
        "",
        "Contexto (2) - con lag 1",
        "  - peso_barrio_en_distrito, peso_barrio_en_ciudad",
        "",
        "Codificación categórica (11)",
        "  - dist_* (one-hot de 10 distritos)",
        "  - barrio_te (target encoding de barrio)",
    ]
    anadir_bullets(slide, items, top=1.8, tamano=11)


def slide_11_fase5(prs):
    slide = nuevo_slide(prs)
    anadir_barra_lateral(slide, prs)
    anadir_titulo(slide, "9. Fase 5: Split temporal")

    anadir_caja_destacada(
        slide,
        "Split TEMPORAL (no aleatorio)\n"
        "Train: 2012-2022  ·  Test: 2023-2025",
        top=1.8, height=1.2,
    )

    items = [
        "Justificación",
        "  - El objetivo es predecir el futuro",
        "  - Un split aleatorio causaría data leakage temporal",
        "  - El modelo debe evaluarse en datos POSTERIORES al train",
        "",
        "Dimensiones",
        "  - Train: 8.908 filas (11 años)",
        "  - Test: 2.448 filas (3 años)",
        "  - Total: 11.356 filas",
        "",
        "Distribución del target (asimetría)",
        "  - Train: media 20,84 · mediana 15",
        "  - Test:  media 28,21 · mediana 22",
        "  - Skewness global: 2,76",
        "  - Justifica el uso de objetivo Poisson en XGBoost",
    ]
    anadir_bullets(slide, items, top=3.3, tamano=13)


def slide_12_leakage(prs):
    slide = nuevo_slide(prs)
    anadir_barra_lateral(slide, prs)
    anadir_titulo(slide, "10. Detección de data leakage", color=RGBColor(0xC0, 0x39, 0x2B))

    anadir_caja_destacada(
        slide,
        "Hallazgo clave del proyecto: data leakage en features de contexto",
        top=1.8, height=1.1, color_fondo=RGBColor(0xC0, 0x39, 0x2B),
    )

    items = [
        "Problema detectado",
        "  - peso_barrio_en_distrito y peso_barrio_en_ciudad",
        "    se calculaban con el TARGET DEL MISMO MES",
        "  - El modelo 'veía' parte de la respuesta correcta",
        "",
        "Síntomas",
        "  - R² inusualmente alto: 0,835 en test",
        "  - Feature importance sospechosa",
        "",
        "Solución aplicada",
        "  - Recalcular TODAS las features de contexto y tipología",
        "    con LAG 1 (mes anterior)",
        "  - Garantiza usar solo información del pasado",
        "",
        "Impacto en el rendimiento",
        "  - R² test: 0,835 → 0,617 (modelo honesto)",
        "  - RMSE test: 10,34 → 15,77",
        "",
        "Lección: el rendimiento cayó, pero el modelo es HONESTO y defendible.",
    ]
    anadir_bullets(slide, items, top=3.2, tamano=11)


def slide_13_modelado(prs):
    slide = nuevo_slide(prs)
    anadir_barra_lateral(slide, prs)
    anadir_titulo(slide, "11. Modelado: Ridge vs XGBoost")

    items = [
        "Baseline (Ridge y Lasso)",
        "  - 15 features numéricas",
        "  - TimeSeriesSplit con 3 folds",
        "  - GridSearchCV sobre el parámetro alpha",
        "  - Ridge: R² = 0,615 · RMSE = 15,82",
        "",
        "Modelo final (XGBoost)",
        "  - 32 features (todas)",
        "  - Objetivo Poisson (datos de conteo)",
        "  - RandomizedSearchCV con grid conservador",
        "  - Hiperparámetros: max_depth=3, reg_lambda=20, min_child_weight=10",
        "  - XGBoost: R² = 0,617 · RMSE = 15,77",
        "",
        "Decisión: XGBoost por:",
        "  - Ligera mejora en RMSE y MAPE",
        "  - Overfitting controlado (delta train-test R² = 0,022)",
        "  - Interpretabilidad superior vía SHAP",
    ]
    anadir_bullets(slide, items, top=1.8, tamano=12)


def slide_14_validacion(prs):
    slide = nuevo_slide(prs)
    anadir_barra_lateral(slide, prs)
    anadir_titulo(slide, "12. Validación temporal")

    items = [
        "Estrategia de validación",
        "  - TimeSeriesSplit con 3 folds durante la búsqueda de hiperparámetros",
        "  - Evaluación final en test (2023-2025)",
        "",
        "Métricas utilizadas",
        "  - RMSE: raíz del error cuadrático medio (escala original)",
        "  - MAE: error absoluto medio (interpretable)",
        "  - R²: coeficiente de determinación",
        "  - MAPE: error porcentual absoluto medio (business)",
        "",
        "Resultados finales del modelo XGBoost",
        "  - Train: RMSE=13,39 · MAE=7,43 · R²=0,639",
        "  - Test:  RMSE=15,77 · MAE=9,26 · R²=0,617 · MAPE=36,7%",
        "",
        "Análisis de overfitting",
        "  - Delta R² train-test: 0,022",
        "  - Delta RMSE: 2,38",
        "  - Overfitting CONTROLADO",
    ]
    anadir_bullets(slide, items, top=1.8, tamano=13)


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("GENERANDO PRESENTACION 1: METODOLOGIA")
    print("=" * 60)

    # Crear presentacion
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Generar slides
    print("\nGenerando 14 slides...")
    slide_01_portada(prs)
    slide_02_indice(prs)
    slide_03_reto(prs)
    slide_04_preguntas(prs)
    slide_05_fuentes(prs)
    slide_06_pipeline(prs)
    slide_07_fase1(prs)
    slide_08_fase2(prs)
    slide_09_fase3(prs)
    slide_10_fase4(prs)
    slide_11_fase5(prs)
    slide_12_leakage(prs)
    slide_13_modelado(prs)
    slide_14_validacion(prs)

    # Guardar
    SALIDA_PPTX.parent.mkdir(parents=True, exist_ok=True)
    prs.save(SALIDA_PPTX)
    print(f"\nPresentacion guardada: {SALIDA_PPTX}")
    print(f"Total slides: {len(prs.slides)}")


if __name__ == "__main__":
    main()