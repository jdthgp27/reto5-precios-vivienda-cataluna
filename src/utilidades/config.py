"""
Configuración central del proyecto.
Rutas, constantes y parámetros globales.
"""
from pathlib import Path

# ============================================================
# RUTAS BASE
# ============================================================
BASE_DIR = Path(r"C:\Users\jdthg\Documents\curso6BI\reto5_precios_vivienda_cataluna")

DATA_DIR = BASE_DIR / "data"
DATA_RAW = DATA_DIR / "raw"
DATA_INTERIM = DATA_DIR / "interim"
DATA_PROCESSED = DATA_DIR / "processed"

RAW_IDESCAT = DATA_RAW / "idescat"
RAW_SERPAVI = DATA_RAW / "serpavi"
RAW_HABIT = DATA_RAW / "habit"
RAW_POBLACION = DATA_RAW / "poblacion"

MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
FIGURAS_DIR = REPORTS_DIR / "figuras"
DOCS_DIR = REPORTS_DIR / "documentacion"
PRESENTACION_DIR = REPORTS_DIR / "presentacion"
METRICAS_DIR = REPORTS_DIR / "metricas"

# ============================================================
# PARÁMETROS DEL PROYECTO
# ============================================================
RANDOM_STATE = 42

TRAIN_YEARS = (2011, 2022)
TEST_YEARS = (2023, 2024)

TARGET = "precio_m2_compraventa"
TARGET_LOG = "log_precio_m2"

N_COMARQUES = 42

# ============================================================
# VERIFICACIÓN
# ============================================================
def verificar_estructura():
    """Comprueba que todas las carpetas existen."""
    rutas = [
        DATA_RAW, DATA_INTERIM, DATA_PROCESSED,
        RAW_IDESCAT, RAW_SERPAVI, RAW_HABIT, RAW_POBLACION,
        MODELS_DIR, FIGURAS_DIR, DOCS_DIR,
        PRESENTACION_DIR, METRICAS_DIR,
    ]
    for ruta in rutas:
        estado = "✅ OK" if ruta.exists() else "⚠️  FALTA"
        print(f"{estado}: {ruta}")


if __name__ == "__main__":
    verificar_estructura()