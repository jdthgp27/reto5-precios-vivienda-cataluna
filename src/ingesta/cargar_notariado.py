"""
Ingesta de los CSV de Notariado (Barcelona ciudad).

Los archivos vienen del portal datos.gob.es, uno por año (2012–2026).
Estructura:
    Any, Mes, Codi_Districte, Nom_Districte, Codi_Barri, Nom_Barri,
    Tipologia_Us_Codi, Tipologia_Us_Desc, num_transacciones

Donde 'num_transacciones' es el número de transmisiones
(o vacío / '..' si es nulo).
"""
from pathlib import Path
import sys
import pandas as pd

# Añadir el directorio raíz al path para poder importar config
sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.utilidades.config import DATA_RAW, DATA_INTERIM


# ============================================================
# CONFIGURACIÓN
# ============================================================
CARPETA_NOTARIADO = DATA_RAW / "notariado_limpio"
ARCHIVO_SALIDA = DATA_INTERIM / "notariado_barcelona.csv"

TIPOLOGIAS = {
    1: "Residencial",
    2: "Aparcament",
    3: "Comercial",
    4: "Oficina",
    5: "Turístic",
    8: "Equipaments",
    9: "No consta",
}


# ============================================================
# FUNCIONES
# ============================================================
def leer_csv(ruta: Path) -> pd.DataFrame:
    """
    Lee un CSV del Notariado ignorando la cabecera original y
    asignando nombres fijos a las columnas.
    Esto es robusto ante comillas mal formadas en el encabezado.
    """
    NOMBRES_COLUMNAS = [
        "Any", "Mes", "Codi_Districte", "Nom_Districte",
        "Codi_Barri", "Nom_Barri",
        "Tipologia_Us_Codi", "Tipologia_Us_Desc",
        "num_transacciones",
    ]

    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            df = pd.read_csv(
                ruta,
                encoding=encoding,
                sep=",",
                skiprows=1,           # Ignorar cabecera original
                header=None,          # Sin cabecera
                names=NOMBRES_COLUMNAS,
                quotechar='"',        # Respetar comillas de texto
            )
            print(f"  OK  {ruta.name} ({len(df)} filas)")
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"  ERR {ruta.name}: {e}")
            return None

    raise ValueError(f"No se pudo leer {ruta} con ninguna codificación")


def corregir_codificacion(df: pd.DataFrame) -> pd.DataFrame:
    """
    Corrige el problema de UTF-8 leído como Latin-1.
    Ejemplo: 'Ciutat Vella' → 'Ciutat Vella'
    """
    columnas_texto = ["Nom_Districte", "Nom_Barri", "Tipologia_Us_Desc"]
    for col in columnas_texto:
        if col in df.columns:
            try:
                df[col] = df[col].astype(str).str.encode("latin-1").str.decode("utf-8")
            except (UnicodeDecodeError, UnicodeEncodeError):
                pass
    return df


def limpiar_transacciones(df: pd.DataFrame) -> pd.DataFrame:
    """
    Asegura que 'num_transacciones' sea numérico.
    Los valores vacíos, '..' o no numéricos → 0.
    """
    if "num_transacciones" not in df.columns:
        raise KeyError(
            f"Falta la columna 'num_transacciones'. "
            f"Columnas encontradas: {df.columns.tolist()}"
        )
    df["num_transacciones"] = pd.to_numeric(
        df["num_transacciones"], errors="coerce"
    ).fillna(0).astype(int)
    return df


def limpiar_tipologia(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza la descripcion de la tipologia desde el codigo."""
    # Limpiar comillas residuales en columnas de texto
    for col in ["Nom_Districte", "Nom_Barri"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip('"')

    # Reconstruir descripcion de tipologia desde el codigo
    df["Tipologia_Us_Codi"] = pd.to_numeric(
        df["Tipologia_Us_Codi"], errors="coerce"
    )
    df["Tipologia_Us_Desc"] = df["Tipologia_Us_Codi"].map(TIPOLOGIAS)
    return df


def procesar_archivo(ruta: Path) -> pd.DataFrame:
    """Pipeline completo para un único CSV."""
    df = leer_csv(ruta)
    if df is None:
        return None
    df = corregir_codificacion(df)
    df = limpiar_transacciones(df)
    df = limpiar_tipologia(df)
    df["archivo_origen"] = ruta.name
    return df


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("INGESTA DE DATOS DEL NOTARIADO - BARCELONA")
    print("=" * 60)

    if not CARPETA_NOTARIADO.exists():
        print(f"❌ No existe la carpeta: {CARPETA_NOTARIADO}")
        return

    archivos = sorted(CARPETA_NOTARIADO.glob("*.csv"))
    print(f"\n📁 Archivos encontrados: {len(archivos)}")
    for a in archivos:
        print(f"   - {a.name}")

    if not archivos:
        print("❌ No hay archivos CSV en la carpeta.")
        return

    print("\n📖 Procesando archivos...")
    dfs = []
    for ruta in archivos:
        df = procesar_archivo(ruta)
        if df is not None:
            dfs.append(df)

    print("\n🔗 Concatenando...")
    df_total = pd.concat(dfs, ignore_index=True)
    print(f"   Total filas: {len(df_total):,}")
    print(f"   Total columnas: {len(df_total.columns)}")

    # Reordenar columnas
    columnas_orden = [
        "Any", "Mes", "Codi_Districte", "Nom_Districte",
        "Codi_Barri", "Nom_Barri",
        "Tipologia_Us_Codi", "Tipologia_Us_Desc",
        "num_transacciones", "archivo_origen",
    ]
    df_total = df_total[columnas_orden]

    # Guardar
    DATA_INTERIM.mkdir(parents=True, exist_ok=True)
    df_total.to_csv(ARCHIVO_SALIDA, index=False, encoding="utf-8")
    print(f"\n💾 Guardado en: {ARCHIVO_SALIDA}")

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE VALIDACIÓN")
    print("=" * 60)
    print(f"\n📅 Años cubiertos: {sorted(df_total['Any'].unique())}")
    print(f"\n🏙️  Distritos ({df_total['Codi_Districte'].nunique()}):")
    for d in sorted(df_total['Nom_Districte'].unique()):
        print(f"   - {d}")
    print(f"\n🏘️  Barrios únicos: {df_total['Codi_Barri'].nunique()}")
    print(f"\n🏷️  Tipologías:")
    for t in sorted(df_total['Tipologia_Us_Desc'].dropna().unique()):
        print(f"   - {t}")
    print(f"\n📊 Transacciones por año:")
    print(df_total.groupby("Any")["num_transacciones"].sum().to_string())
    print(f"\n📊 Top 10 barrios por transacciones totales:")
    top = (df_total.groupby("Nom_Barri")["num_transacciones"]
           .sum().sort_values(ascending=False).head(10))
    print(top.to_string())


if __name__ == "__main__":
    main()