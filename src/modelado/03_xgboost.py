# 03_xgboost.py
# Modelo XGBoost con objetivo Poisson para prediccion de
# transacciones inmobiliarias por barrio-mes en Barcelona.
#
# Entrada:
#   data/processed/train.csv
#   data/processed/test.csv
#
# Salidas:
#   models/xgboost_final.json
#   models/xgboost_metricas.json
#   models/feature_importance.csv
#   reports/metricas/comparativa_xgboost.csv
#   reports/figuras/10_xgboost_importancia.png
#   reports/figuras/11_xgboost_predicciones.png
#   data/processed/predicciones_xgboost.csv

from pathlib import Path
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import xgboost as xgb
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score
)
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.utilidades.config import (
    DATA_PROCESSED, MODELS_DIR, METRICAS_DIR, FIGURAS_DIR
)


TRAIN_PATH = DATA_PROCESSED / "train.csv"
TEST_PATH = DATA_PROCESSED / "test.csv"

SALIDA_MODELO = MODELS_DIR / "xgboost_final.json"
SALIDA_METRICAS = MODELS_DIR / "xgboost_metricas.json"
SALIDA_IMPORTANCIA = MODELS_DIR / "feature_importance.csv"
SALIDA_COMPARATIVA = METRICAS_DIR / "comparativa_xgboost.csv"
SALIDA_PREDICCIONES = DATA_PROCESSED / "predicciones_xgboost.csv"

FIGURA_IMPORTANCIA = FIGURAS_DIR / "10_xgboost_importancia.png"
FIGURA_PREDICCIONES = FIGURAS_DIR / "11_xgboost_predicciones.png"

TARGET = "total_transacciones"

# Columnas que NO son features del modelo
COLUMNAS_EXCLUIR = ["Any", "Mes", "Nom_Barri", TARGET]


# ============================================================
# UTILIDADES
# ============================================================
def calcular_metricas(y_true, y_pred, nombre="XGBoost"):
    """Calcula RMSE, MAE, R2, MAPE."""
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    mask = y_true > 0
    if mask.sum() > 0:
        mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    else:
        mape = np.nan
    return {
        "modelo": nombre,
        "rmse": round(rmse, 3),
        "mae": round(mae, 3),
        "r2": round(r2, 4),
        "mape": round(mape, 2) if not np.isnan(mape) else None,
    }


# ============================================================
# HYPERPARAMETER TUNING
# ============================================================
def buscar_hiperparametros(X_train, y_train):
    """Busca los mejores hiperparametros con RandomizedSearchCV."""
    print("\nBuscando mejores hiperparametros...")

    param_dist = {
        "n_estimators": [200, 400, 600],
        "max_depth": [3, 5, 7, 9],
        "learning_rate": [0.01, 0.03, 0.05, 0.1],
        "subsample": [0.7, 0.8, 0.9, 1.0],
        "colsample_bytree": [0.7, 0.8, 0.9, 1.0],
        "reg_alpha": [0, 0.1, 1.0],
        "reg_lambda": [0.5, 1.0, 3.0, 5.0],
        "min_child_weight": [1, 3, 5, 7],
    }

    # Modelo base
    xgb_model = xgb.XGBRegressor(
        objective="count:poisson",
        random_state=42,
        tree_method="hist",
        n_jobs=-1,
    )

    # TimeSeriesSplit
    tscv = TimeSeriesSplit(n_splits=3)

    search = RandomizedSearchCV(
        xgb_model,
        param_dist,
        n_iter=25,
        cv=tscv,
        scoring="neg_root_mean_squared_error",
        random_state=42,
        n_jobs=-1,
        verbose=1,
    )

    search.fit(X_train, y_train)

    print(f"\n  Mejores parametros:")
    for k, v in search.best_params_.items():
        print(f"    {k}: {v}")
    print(f"  Mejor RMSE CV: {-search.best_score_:.3f}")

    return search.best_estimator_, search.best_params_


# ============================================================
# VISUALIZACIONES
# ============================================================
def grafico_importancia(importancias: pd.DataFrame):
    """Grafico de barras con las 20 features mas importantes."""
    fig, ax = plt.subplots(figsize=(11, 9))

    top20 = importancias.head(20)
    sns.barplot(
        data=top20, y="feature", x="importance",
        hue="feature", palette="viridis", legend=False, ax=ax,
    )
    ax.set_title("Top 20 features mas importantes - XGBoost")
    ax.set_xlabel("Importancia")
    ax.set_ylabel("")

    plt.tight_layout()
    plt.savefig(FIGURA_IMPORTANCIA, bbox_inches="tight", dpi=110)
    plt.close()
    print(f"  Figura guardada: {FIGURA_IMPORTANCIA.name}")


def grafico_predicciones(y_true, y_pred):
    """Scatter de predicciones vs valores reales + residuos."""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Scatter predicciones vs real
    axes[0].scatter(y_true, y_pred, alpha=0.3, s=15, color="#2E86AB")
    max_val = max(y_true.max(), y_pred.max())
    axes[0].plot([0, max_val], [0, max_val], "r--", linewidth=1.5, label="y = x")
    axes[0].set_title("Predicciones vs Valores reales")
    axes[0].set_xlabel("Valores reales")
    axes[0].set_ylabel("Predicciones")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Residuos
    residuos = y_true - y_pred
    axes[1].scatter(y_pred, residuos, alpha=0.3, s=15, color="#F18F01")
    axes[1].axhline(0, color="red", linestyle="--", linewidth=1.5)
    axes[1].set_title("Residuos vs Predicciones")
    axes[1].set_xlabel("Predicciones")
    axes[1].set_ylabel("Residuos (real - pred)")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURA_PREDICCIONES, bbox_inches="tight", dpi=110)
    plt.close()
    print(f"  Figura guardada: {FIGURA_PREDICCIONES.name}")


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("XGBOOST - MODELO PRINCIPAL")
    print("=" * 60)

    # Cargar
    print("\nCargando datos...")
    train = pd.read_csv(TRAIN_PATH)
    test = pd.read_csv(TEST_PATH)
    print(f"  Train: {train.shape}")
    print(f"  Test: {test.shape}")

    # Features
    FEATURES = [c for c in train.columns if c not in COLUMNAS_EXCLUIR]
    print(f"\nFeatures del modelo: {len(FEATURES)}")

    X_train = train[FEATURES].values
    y_train = train[TARGET].values
    X_test = test[FEATURES].values
    y_test = test[TARGET].values

    # 1. Búsqueda de hiperparámetros
    modelo, mejores_params = buscar_hiperparametros(X_train, y_train)

    # 2. Evaluación en test
    print("\nEvaluando en test...")
    y_pred_train = modelo.predict(X_train)
    y_pred_test = modelo.predict(X_test)

    metricas_train = calcular_metricas(y_train, y_pred_train, "XGBoost (train)")
    metricas_test = calcular_metricas(y_test, y_pred_test, "XGBoost (test)")

    print(f"\n  Train: RMSE={metricas_train['rmse']:.3f}, "
          f"MAE={metricas_train['mae']:.3f}, R2={metricas_train['r2']:.4f}")
    print(f"  Test:  RMSE={metricas_test['rmse']:.3f}, "
          f"MAE={metricas_test['mae']:.3f}, R2={metricas_test['r2']:.4f}")

    # 3. Guardar modelo
    modelo.save_model(SALIDA_MODELO)
    print(f"\n  Modelo guardado: {SALIDA_MODELO.name}")

    # 4. Feature importance
    importancias = pd.DataFrame({
        "feature": FEATURES,
        "importance": modelo.feature_importances_,
    }).sort_values("importance", ascending=False).reset_index(drop=True)
    importancias.to_csv(SALIDA_IMPORTANCIA, index=False)
    print(f"  Importancias guardadas: {SALIDA_IMPORTANCIA.name}")

    # 5. Metricas
    with open(SALIDA_METRICAS, "w") as f:
        json.dump({
            "mejores_params": mejores_params,
            "train": metricas_train,
            "test": metricas_test,
        }, f, indent=2)
    print(f"  Metricas guardadas: {SALIDA_METRICAS.name}")

    # 6. Predicciones para analisis posterior
    predicciones = test[["Any", "Mes", "Nom_Barri", TARGET]].copy()
    predicciones["prediccion"] = y_pred_test
    predicciones["residuo"] = predicciones[TARGET] - predicciones["prediccion"]
    predicciones.to_csv(SALIDA_PREDICCIONES, index=False)
    print(f"  Predicciones guardadas: {SALIDA_PREDICCIONES.name}")

    # 7. Graficos
    print("\nGenerando graficos...")
    grafico_importancia(importancias)
    grafico_predicciones(y_test, y_pred_test)

    # 8. Tabla comparativa con baseline
    df_baseline = pd.read_csv(METRICAS_DIR / "comparativa_baseline.csv")
    df_xgb = pd.DataFrame([metricas_test])
    df_comparativa = pd.concat([df_baseline, df_xgb], ignore_index=True)
    df_comparativa.to_csv(SALIDA_COMPARATIVA, index=False)

    print("\n" + "=" * 60)
    print("COMPARATIVA FINAL")
    print("=" * 60)
    print(df_comparativa.to_string(index=False))

    # 9. Mejora sobre baseline
    mejor_baseline = df_baseline.loc[df_baseline["rmse"].idxmin()]
    mejora_rmse = (mejor_baseline["rmse"] - metricas_test["rmse"]) / mejor_baseline["rmse"] * 100
    mejora_r2 = metricas_test["r2"] - mejor_baseline["r2"]

    print("\n" + "=" * 60)
    print("MEJORA SOBRE EL BASELINE")
    print("=" * 60)
    print(f"  Mejor baseline: {mejor_baseline['modelo']} (RMSE={mejor_baseline['rmse']})")
    print(f"  XGBoost:        RMSE={metricas_test['rmse']}")
    print(f"  Mejora en RMSE: {mejora_rmse:.2f}%")
    print(f"  Delta R2:       {mejora_r2:+.4f}")


if __name__ == "__main__":
    main()