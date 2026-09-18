# 02_baseline.py
# Modelos baseline para prediccion de transacciones inmobiliarias.
#
# Entrada:
#   data/processed/train.csv
#   data/processed/test.csv
#
# Salidas:
#   reports/metricas/comparativa_baseline.csv
#   reports/figuras/09_comparativa_baseline.png
#   models/ridge_baseline.pkl
#   models/lasso_baseline.pkl
#   models/scaler_baseline.pkl

from pathlib import Path
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.linear_model import Ridge, Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.utilidades.config import (
    DATA_PROCESSED, MODELS_DIR, METRICAS_DIR, FIGURAS_DIR
)


TRAIN_PATH = DATA_PROCESSED / "train.csv"
TEST_PATH = DATA_PROCESSED / "test.csv"

SALIDA_METRICAS = METRICAS_DIR / "comparativa_baseline.csv"
SALIDA_FIGURA = FIGURAS_DIR / "09_comparativa_baseline.png"
SALIDA_RIDGE = MODELS_DIR / "ridge_baseline.pkl"
SALIDA_LASSO = MODELS_DIR / "lasso_baseline.pkl"
SALIDA_SCALER = MODELS_DIR / "scaler_baseline.pkl"

TARGET = "total_transacciones"

# Features del baseline (solo numericas)
FEATURES = [
    "Mes", "Any", "mes_sin", "mes_cos", "es_agosto", "tendencia",
    "lag_1", "lag_2", "lag_3", "lag_12",
    "rolling_3m", "rolling_6m", "rolling_12m", "diff_1",
    "barrio_te",
]


# ============================================================
# UTILIDADES
# ============================================================
def calcular_metricas(y_true, y_pred, nombre_modelo):
    """Calcula RMSE, MAE, R2, MAPE."""
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    # MAPE: cuidado con valores 0
    mask = y_true > 0
    if mask.sum() > 0:
        mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    else:
        mape = np.nan

    return {
        "modelo": nombre_modelo,
        "rmse": round(rmse, 3),
        "mae": round(mae, 3),
        "r2": round(r2, 4),
        "mape": round(mape, 2) if not np.isnan(mape) else None,
    }


# ============================================================
# MODELOS
# ============================================================
def modelo_dummy_media(y_train, y_test):
    """Predice siempre la media del train."""
    media = y_train.mean()
    y_pred = np.full(len(y_test), media)
    return y_pred, {"media_train": float(media)}


def modelo_dummy_rolling(y_train_df, y_test_df):
    """
    Predice la media de los ultimos 12 meses del mismo barrio
    (mas listo que la media global). Si no hay historia, usa media global.
    """
    medias = y_train_df.groupby("Nom_Barri")[TARGET].mean()
    y_pred = y_test_df["Nom_Barri"].map(medias).fillna(y_train_df[TARGET].mean())
    return y_pred.values, {"medias_por_barrio": len(medias)}


def entrenar_ridge_con_cv(X_train, y_train):
    """Entrena Ridge con validacion cruzada temporal."""
    print("  Entrenando Ridge con TimeSeriesSplit...")

    # Escalar
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)

    # Grid search de alpha
    tscv = TimeSeriesSplit(n_splits=3)
    param_grid = {"alpha": [0.01, 0.1, 1.0, 10.0, 100.0]}

    ridge = Ridge(random_state=42)
    grid = GridSearchCV(
        ridge, param_grid, cv=tscv,
        scoring="neg_root_mean_squared_error", n_jobs=-1,
    )
    grid.fit(X_scaled, y_train)

    print(f"    Mejor alpha: {grid.best_params_['alpha']}")
    print(f"    Mejor RMSE CV: {-grid.best_score_:.3f}")

    return grid.best_estimator_, scaler, grid.best_params_


def entrenar_lasso_con_cv(X_train, y_train):
    """Entrena Lasso con validacion cruzada temporal."""
    print("  Entrenando Lasso con TimeSeriesSplit...")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)

    tscv = TimeSeriesSplit(n_splits=3)
    param_grid = {"alpha": [0.01, 0.05, 0.1, 0.5, 1.0, 5.0]}

    lasso = Lasso(random_state=42, max_iter=10000)
    grid = GridSearchCV(
        lasso, param_grid, cv=tscv,
        scoring="neg_root_mean_squared_error", n_jobs=-1,
    )
    grid.fit(X_scaled, y_train)

    print(f"    Mejor alpha: {grid.best_params_['alpha']}")
    print(f"    Mejor RMSE CV: {-grid.best_score_:.3f}")

    return grid.best_estimator_, scaler, grid.best_params_


# ============================================================
# VISUALIZACION
# ============================================================
def crear_grafico_comparativa(df_metricas):
    """Crea grafico de barras comparando modelos."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # RMSE
    sns.barplot(data=df_metricas, x="modelo", y="rmse",
                hue="modelo", palette="viridis", legend=False, ax=axes[0])
    axes[0].set_title("RMSE (menor es mejor)")
    axes[0].set_xlabel("")
    axes[0].tick_params(axis="x", rotation=15)

    # MAE
    sns.barplot(data=df_metricas, x="modelo", y="mae",
                hue="modelo", palette="viridis", legend=False, ax=axes[1])
    axes[1].set_title("MAE (menor es mejor)")
    axes[1].set_xlabel("")
    axes[1].tick_params(axis="x", rotation=15)

    # R2
    sns.barplot(data=df_metricas, x="modelo", y="r2",
                hue="modelo", palette="coolwarm", legend=False, ax=axes[2])
    axes[2].set_title("R2 (mayor es mejor)")
    axes[2].set_xlabel("")
    axes[2].axhline(0, color="black", linestyle="--", linewidth=0.8)
    axes[2].tick_params(axis="x", rotation=15)

    plt.tight_layout()
    plt.savefig(SALIDA_FIGURA, bbox_inches="tight", dpi=110)
    plt.close()
    print(f"\n  Figura guardada: {SALIDA_FIGURA}")


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("BASELINE - MODELOS DE REFERENCIA")
    print("=" * 60)

    # Crear directorios si no existen
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    METRICAS_DIR.mkdir(parents=True, exist_ok=True)

    # Cargar
    print("\nCargando datos...")
    train = pd.read_csv(TRAIN_PATH)
    test = pd.read_csv(TEST_PATH)
    print(f"  Train: {train.shape}")
    print(f"  Test: {test.shape}")

    X_train = train[FEATURES].values
    y_train = train[TARGET].values
    X_test = test[FEATURES].values
    y_test = test[TARGET].values

    print(f"\nFeatures del baseline: {len(FEATURES)}")
    print(f"  {FEATURES}")

    resultados = []

    # ---------------------------------------------------------
    # 1. Dummy: media del train
    # ---------------------------------------------------------
    print("\n[1/4] Dummy - Media del train...")
    y_pred_dummy, meta_dummy = modelo_dummy_media(y_train, y_test)
    metricas = calcular_metricas(y_test, y_pred_dummy, "Dummy (media)")
    print(f"  RMSE: {metricas['rmse']:.3f}, MAE: {metricas['mae']:.3f}, "
          f"R2: {metricas['r2']:.4f}")
    resultados.append(metricas)

    # ---------------------------------------------------------
    # 2. Dummy: media por barrio
    # ---------------------------------------------------------
    print("\n[2/4] Dummy - Media por barrio...")
    y_pred_dummy2, meta_dummy2 = modelo_dummy_rolling(train, test)
    metricas = calcular_metricas(y_test, y_pred_dummy2, "Dummy (media barrio)")
    print(f"  RMSE: {metricas['rmse']:.3f}, MAE: {metricas['mae']:.3f}, "
          f"R2: {metricas['r2']:.4f}")
    resultados.append(metricas)

    # ---------------------------------------------------------
    # 3. Ridge
    # ---------------------------------------------------------
    print("\n[3/4] Ridge...")
    ridge_model, scaler_ridge, params_ridge = entrenar_ridge_con_cv(X_train, y_train)
    X_test_scaled = scaler_ridge.transform(X_test)
    y_pred_ridge = ridge_model.predict(X_test_scaled)
    metricas = calcular_metricas(y_test, y_pred_ridge, "Ridge")
    print(f"  RMSE: {metricas['rmse']:.3f}, MAE: {metricas['mae']:.3f}, "
          f"R2: {metricas['r2']:.4f}")
    resultados.append(metricas)

    joblib.dump(ridge_model, SALIDA_RIDGE)
    joblib.dump(scaler_ridge, SALIDA_SCALER)
    print(f"  Modelo guardado: {SALIDA_RIDGE}")

    # ---------------------------------------------------------
    # 4. Lasso
    # ---------------------------------------------------------
    print("\n[4/4] Lasso...")
    lasso_model, scaler_lasso, params_lasso = entrenar_lasso_con_cv(X_train, y_train)
    X_test_scaled = scaler_lasso.transform(X_test)
    y_pred_lasso = lasso_model.predict(X_test_scaled)
    metricas = calcular_metricas(y_test, y_pred_lasso, "Lasso")
    print(f"  RMSE: {metricas['rmse']:.3f}, MAE: {metricas['mae']:.3f}, "
          f"R2: {metricas['r2']:.4f}")
    resultados.append(metricas)

    joblib.dump(lasso_model, SALIDA_LASSO)
    print(f"  Modelo guardado: {SALIDA_LASSO}")

    # ---------------------------------------------------------
    # Comparativa
    # ---------------------------------------------------------
    df_metricas = pd.DataFrame(resultados)
    print("\n" + "=" * 60)
    print("COMPARATIVA DE MODELOS BASELINE")
    print("=" * 60)
    print(df_metricas.to_string(index=False))

    df_metricas.to_csv(SALIDA_METRICAS, index=False)
    print(f"\n  Metricas guardadas: {SALIDA_METRICAS}")

    # Grafico
    crear_grafico_comparativa(df_metricas)

    # Analisis del mejor modelo
    mejor = df_metricas.loc[df_metricas["rmse"].idxmin()]
    print("\n" + "=" * 60)
    print(f"MEJOR MODELO: {mejor['modelo']}")
    print(f"  RMSE: {mejor['rmse']}")
    print(f"  MAE:  {mejor['mae']}")
    print(f"  R2:   {mejor['r2']}")
    print(f"  MAPE: {mejor['mape']}%")
    print("=" * 60)


if __name__ == "__main__":
    main()