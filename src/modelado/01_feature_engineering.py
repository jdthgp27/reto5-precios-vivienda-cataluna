# 01_feature_engineering.py
# Construccion de features para el modelo de prediccion de
# transacciones inmobiliarias por barrio-mes en Barcelona.
#
# Entrada:
#   data/processed/barcelona_barrio_mes_filtrado.csv
#   data/processed/barcelona_barrio_mes_tipologia_filtrado.csv
#
# Salidas:
#   data/processed/dataset_modelado.csv
#   data/processed/train.csv
#   data/processed/test.csv

from pathlib import Path
import sys
import pandas as pd
import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.utilidades.config import DATA_PROCESSED


ARCHIVO_VISTA1 = DATA_PROCESSED / "barcelona_barrio_mes_filtrado.csv"
ARCHIVO_VISTA2 = DATA_PROCESSED / "barcelona_barrio_mes_tipologia_filtrado.csv"

SALIDA_DATASET = DATA_PROCESSED / "dataset_modelado.csv"
SALIDA_TRAIN = DATA_PROCESSED / "train.csv"
SALIDA_TEST = DATA_PROCESSED / "test.csv"

# Split temporal
ANYO_CORTE = 2023  # Train: <2023, Test: >=2023

# Lags a crear
LAGS = [1, 2, 3, 12]
ROLLING_WINDOWS = [3, 6, 12]


# ============================================================
# CARGA
# ============================================================
def cargar_datos():
    print("Cargando datos...")
    df = pd.read_csv(ARCHIVO_VISTA1, parse_dates=["fecha"])
    df_tipo = pd.read_csv(ARCHIVO_VISTA2, parse_dates=["fecha"])
    print(f"  Vista 1: {len(df):,} filas")
    print(f"  Vista 2: {len(df_tipo):,} filas")
    return df, df_tipo


# ============================================================
# FEATURES TEMPORALES
# ============================================================
def crear_features_temporales(df: pd.DataFrame) -> pd.DataFrame:
    """Crea features de calendario y ciclicas."""
    print("\nCreando features temporales...")

    # Mes ciclico (sin/cos para capturar estacionalidad suave)
    df["mes_sin"] = np.sin(2 * np.pi * df["Mes"] / 12)
    df["mes_cos"] = np.cos(2 * np.pi * df["Mes"] / 12)

    # Trimestre
    df["trimestre"] = ((df["Mes"] - 1) // 3) + 1

    # Tendencia (anos desde 2012)
    df["tendencia"] = df["Any"] - 2012

    # Es agosto (mes atipico)
    df["es_agosto"] = (df["Mes"] == 8).astype(int)

    print(f"  Anyadidas: mes_sin, mes_cos, trimestre, tendencia, es_agosto")
    return df


# ============================================================
# LAGS Y ROLLING
# ============================================================
def crear_lags_y_rolling(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea lags y medias moviles por barrio.
    IMPORTANTE: los lags se calculan POR BARRIO, agrupando por Nom_Barri,
    y desplazando en el tiempo segun la columna fecha.
    """
    print("\nCreando lags y rolling windows...")

    # Ordenar por barrio y fecha para que los shifts sean correctos
    df = df.sort_values(["Nom_Barri", "fecha"]).reset_index(drop=True)

    # Lags por barrio
    for lag in LAGS:
        df[f"lag_{lag}"] = (
            df.groupby("Nom_Barri")["total_transacciones"]
            .shift(lag)
        )
        print(f"  lag_{lag} creado")

    # Rolling windows (media movil)
    for w in ROLLING_WINDOWS:
        df[f"rolling_{w}m"] = (
            df.groupby("Nom_Barri")["total_transacciones"]
            .transform(lambda x: x.shift(1).rolling(w, min_periods=1).mean())
        )
        print(f"  rolling_{w}m creado")

    # Diferencia (cambio respecto al mes anterior)
    df["diff_1"] = df["lag_1"] - df["lag_2"]

    # Rellenar NaN de los primeros lags (necesarios para el modelo)
    # Los lags 1-3 tienen NaN en los primeros meses de cada barrio
    # Los rellenamos con 0 (o media del barrio). Aqui: 0
    columnas_lag = [f"lag_{l}" for l in LAGS] + \
                   [f"rolling_{w}m" for w in ROLLING_WINDOWS] + ["diff_1"]
    df[columnas_lag] = df[columnas_lag].fillna(0)

    return df


# ============================================================
# FEATURES DE CONTEXTO (tipologias)
# ============================================================
def crear_features_tipologia(df: pd.DataFrame, df_tipo: pd.DataFrame) -> pd.DataFrame:
    """
    Anade la proporcion de cada tipologia por barrio-mes,
    desplazada UN MES para evitar leakage.
    """
    print("\nCreando features de tipologia (con lag 1)...")

    pivot = df_tipo.pivot_table(
        index=["Nom_Barri", "fecha"],
        columns="Tipologia_Us_Desc",
        values="num_transacciones",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    tipologias = [c for c in pivot.columns if c not in ["Nom_Barri", "fecha"]]
    total = pivot[tipologias].sum(axis=1).replace(0, 1)

    for t in tipologias:
        col_name = f"pct_{t.lower().replace(' ', '_')}"
        pivot[col_name] = pivot[t] / total

    cols_pct = [c for c in pivot.columns if c.startswith("pct_")]
    pivot = pivot[["Nom_Barri", "fecha"] + cols_pct]

    # Ordenar y aplicar shift por barrio
    pivot = pivot.sort_values(["Nom_Barri", "fecha"]).reset_index(drop=True)
    for col in cols_pct:
        pivot[col] = pivot.groupby("Nom_Barri")[col].shift(1)

    # Rellenar NaN (primer mes de cada barrio)
    pivot[cols_pct] = pivot[cols_pct].fillna(0)

    # Merge con df
    df = df.merge(pivot, on=["Nom_Barri", "fecha"], how="left")
    df[cols_pct] = df[cols_pct].fillna(0)

    print(f"  Anadidas: {len(cols_pct)} columnas de tipologias (con lag 1)")
    return df

# ============================================================
# FEATURES DE CONTEXTO (peso del barrio en su distrito)
# ============================================================
def crear_features_contexto(df: pd.DataFrame) -> pd.DataFrame:
    """Anade features de contexto del barrio, calculadas con LAG 1 para evitar leakage."""
    print("\nCreando features de contexto...")

    # Ordenar para que los shifts sean correctos
    df = df.sort_values(["Nom_Barri", "fecha"]).reset_index(drop=True)

    # Peso del barrio en su distrito el MES ANTERIOR
    total_distrito = (
        df.groupby(["Nom_Districte", "fecha"])["total_transacciones"]
        .transform("sum")
    )
    ratio_actual = df["total_transacciones"] / total_distrito.replace(0, 1)
    # Shift dentro de cada barrio
    df["peso_barrio_en_distrito"] = (
        df.groupby("Nom_Barri")
        .apply(lambda g: ratio_actual.loc[g.index].shift(1))
        .reset_index(level=0, drop=True)
        .sort_index()
    )

    # Peso del barrio en Barcelona el MES ANTERIOR
    total_ciudad = df.groupby("fecha")["total_transacciones"].transform("sum")
    ratio_ciudad = df["total_transacciones"] / total_ciudad.replace(0, 1)
    df["peso_barrio_en_ciudad"] = (
        df.groupby("Nom_Barri")
        .apply(lambda g: ratio_ciudad.loc[g.index].shift(1))
        .reset_index(level=0, drop=True)
        .sort_index()
    )

    # Rellenar NaN (primer mes de cada barrio) con 0
    df["peso_barrio_en_distrito"] = df["peso_barrio_en_distrito"].fillna(0)
    df["peso_barrio_en_ciudad"] = df["peso_barrio_en_ciudad"].fillna(0)

    print(f"  Anadidas: peso_barrio_en_distrito, peso_barrio_en_ciudad (con lag 1)")
    return df

# ============================================================
# CODIFICACION DE CATEGORICAS
# ============================================================
def codificar_categoricas(df: pd.DataFrame):
    """
    Codifica Nom_Districte con one-hot.
    Devuelve df codificado y el mapping de target encoding para barrio.
    """
    print("\nCodificando categoricas...")

    # One-hot de distrito
    dummies_distrito = pd.get_dummies(df["Nom_Districte"], prefix="dist")
    df = pd.concat([df, dummies_distrito], axis=1)
    print(f"  One-hot distrito: {dummies_distrito.shape[1]} columnas")

    # Target encoding de barrio: media de transacciones historica
    # IMPORTANTE: se calcula sobre train (evitar leakage)
    target_encoding_barrio = (
        df[df["Any"] < ANYO_CORTE]
        .groupby("Nom_Barri")["total_transacciones"]
        .mean()
        .to_dict()
    )
    df["barrio_te"] = df["Nom_Barri"].map(target_encoding_barrio)
    print(f"  Target encoding barrio: {len(target_encoding_barrio)} valores")

    return df


# ============================================================
# PREPARAR DATASET FINAL
# ============================================================
def preparar_dataset_final(df: pd.DataFrame) -> pd.DataFrame:
    """Selecciona las columnas finales y ordena."""
    print("\nPreparando dataset final...")

    # Columnas que NO son features
    columnas_excluir = [
        "Nom_Barri", "Nom_Districte", "fecha", "archivo_origen",
        "Codi_Districte", "Codi_Barri",
    ]
    # Nota: mantenemos Nom_Barri para trazabilidad en train/test,
    # pero no como feature del modelo

    # Columnas de features
    features = [c for c in df.columns if c not in columnas_excluir]

    # Ordenar: target primero, luego features
    orden = ["Any", "Mes", "Nom_Barri", "total_transacciones"] + \
            [c for c in features if c not in ["Any", "Mes", "total_transacciones"]]

    df = df[orden].sort_values(["Any", "Mes", "Nom_Barri"]).reset_index(drop=True)

    print(f"  Columnas totales: {len(df.columns)}")
    print(f"  Features del modelo: {len(df.columns) - 3}")  # -Any -Mes -Nom_Barri
    return df


# ============================================================
# SPLIT TEMPORAL
# ============================================================
def split_temporal(df: pd.DataFrame):
    """Split temporal: train <2023, test >=2023."""
    print(f"\nSplit temporal (corte: {ANYO_CORTE})...")

    train = df[df["Any"] < ANYO_CORTE].copy()
    test = df[df["Any"] >= ANYO_CORTE].copy()

    print(f"  Train: {len(train):,} filas ({train['Any'].min()}-{train['Any'].max()})")
    print(f"  Test:  {len(test):,} filas ({test['Any'].min()}-{test['Any'].max()})")

    return train, test


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("FEATURE ENGINEERING - BARCELONA")
    print("=" * 60)

    # 1. Cargar
    df, df_tipo = cargar_datos()

    # 2. Features temporales
    df = crear_features_temporales(df)

    # 3. Lags y rolling
    df = crear_lags_y_rolling(df)

    # 4. Tipologias
    df = crear_features_tipologia(df, df_tipo)

    # 5. Contexto
    df = crear_features_contexto(df)

    # 6. Codificacion
    df = codificar_categoricas(df)

    # 7. Dataset final
    df = preparar_dataset_final(df)

    # 8. Split
    train, test = split_temporal(df)

    # 9. Guardar
    df.to_csv(SALIDA_DATASET, index=False, encoding="utf-8")
    train.to_csv(SALIDA_TRAIN, index=False, encoding="utf-8")
    test.to_csv(SALIDA_TEST, index=False, encoding="utf-8")

    print(f"\nGuardado:")
    print(f"  {SALIDA_DATASET}")
    print(f"  {SALIDA_TRAIN}")
    print(f"  {SALIDA_TEST}")

    # 10. Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"\nDataset completo: {df.shape}")
    print(f"Train: {train.shape}")
    print(f"Test: {test.shape}")
    print(f"\nPrimeras columnas de features:")
    print([c for c in df.columns[:25]])
    print(f"... y {len(df.columns) - 25} columnas mas")


if __name__ == "__main__":
    main()