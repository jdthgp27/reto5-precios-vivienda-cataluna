# 05_shap.py
# Analisis de interpretabilidad con SHAP sobre el modelo XGBoost final.
#
# Entrada:
#   models/xgboost_final.json
#   data/processed/train.csv
#   data/processed/test.csv
#
# Salidas:
#   reports/figuras/15_shap_summary.png
#   reports/figuras/16_shap_bar.png
#   reports/figuras/17_shap_dependence_top3.png
#   reports/figuras/18_shap_waterfall.png
#   reports/figuras/19_shap_heatmap.png
#   models/shap_values.pkl

from pathlib import Path
import sys
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb
import shap

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.utilidades.config import (
    DATA_PROCESSED, MODELS_DIR, FIGURAS_DIR
)


MODELO_PATH = MODELS_DIR / "xgboost_final.json"
TRAIN_PATH = DATA_PROCESSED / "train.csv"
TEST_PATH = DATA_PROCESSED / "test.csv"

FIG_SUMMARY = FIGURAS_DIR / "15_shap_summary.png"
FIG_BAR = FIGURAS_DIR / "16_shap_bar.png"
FIG_DEPENDENCE = FIGURAS_DIR / "17_shap_dependence_top3.png"
FIG_WATERFALL = FIGURAS_DIR / "18_shap_waterfall.png"
FIG_HEATMAP = FIGURAS_DIR / "19_shap_heatmap.png"

SALIDA_SHAP = MODELS_DIR / "shap_values.pkl"

TARGET = "total_transacciones"
COLUMNAS_EXCLUIR = ["Any", "Mes", "Nom_Barri", TARGET]


# ============================================================
# CARGA
# ============================================================
def cargar_modelo_y_datos():
    print("Cargando modelo XGBoost...")
    modelo = xgb.XGBRegressor()
    modelo.load_model(MODELO_PATH)
    print(f"  Modelo cargado: {MODELO_PATH.name}")

    print("\nCargando datos...")
    train = pd.read_csv(TRAIN_PATH)
    test = pd.read_csv(TEST_PATH)
    print(f"  Train: {train.shape}")
    print(f"  Test:  {test.shape}")

    # Features
    FEATURES = [c for c in train.columns if c not in COLUMNAS_EXCLUIR]
    print(f"  Features: {len(FEATURES)}")

    X_train = train[FEATURES]
    X_test = test[FEATURES]
    y_test = test[TARGET].values

    return modelo, X_train, X_test, y_test, FEATURES


# ============================================================
# CALCULAR SHAP VALUES
# ============================================================
def calcular_shap(modelo, X_train, X_test):
    """
    Calcula SHAP values usando TreeExplainer.
    Incluye WORKAROUND para xgboost 3.x que devuelve base_score como string.
    """
    import re

    print("\nCalculando SHAP values...")

    # WORKAROUND xgboost 3.x: parchear base_score
    try:
        booster = modelo.get_booster()
        base_score_str = booster.attributes().get('base_score', '[0.5]')
        match = re.search(r'[\d.]+', str(base_score_str))
        if match:
            base_score_float = float(match.group())
            booster.set_attr(base_score=str(base_score_float))
            print(f"  base_score parcheado: {base_score_float}")
    except Exception as e:
        print(f"  Aviso: no se pudo parchear base_score ({e})")

    print("  Usando TreeExplainer (tree_path_dependent)")
    explainer = shap.TreeExplainer(modelo)

    print(f"  Calculando SHAP para {len(X_test)} filas de test...")
    shap_values = explainer(X_test)

    print(f"  SHAP values calculados: shape={shap_values.values.shape}")
    return explainer, shap_values

# ============================================================
# VISUALIZACIONES SHAP
# ============================================================
def grafico_summary(shap_values):
    """Beeswarm plot: impacto de cada feature en cada prediccion."""
    print("\n  Generando summary plot (beeswarm)...")

    plt.figure(figsize=(11, 9))
    shap.summary_plot(shap_values, show=False, max_display=20)
    plt.title("SHAP Summary Plot - Impacto de cada feature", fontsize=13, pad=15)
    plt.tight_layout()
    plt.savefig(FIG_SUMMARY, bbox_inches="tight", dpi=110)
    plt.close()
    print(f"    Guardada: {FIG_SUMMARY.name}")


def grafico_bar(shap_values):
    """Bar plot: importancia media absoluta."""
    print("  Generando bar plot (importancia media)...")

    plt.figure(figsize=(11, 9))
    shap.summary_plot(shap_values, plot_type="bar", show=False, max_display=20)
    plt.title("SHAP Feature Importance - Importancia media", fontsize=13, pad=15)
    plt.tight_layout()
    plt.savefig(FIG_BAR, bbox_inches="tight", dpi=110)
    plt.close()
    print(f"    Guardada: {FIG_BAR.name}")


def grafico_dependence(shap_values, top_features: list):
    """Dependence plots para las top N features (API SHAP nueva)."""
    print(f"  Generando dependence plots para top {len(top_features)}...")

    fig, axes = plt.subplots(1, len(top_features), figsize=(6 * len(top_features), 5))
    if len(top_features) == 1:
        axes = [axes]

    for ax, feat in zip(axes, top_features):
        # API nueva: pasar el Explanation completo y el nombre de la feature
        shap.plots.scatter(shap_values[:, feat], ax=ax, show=False)
        ax.set_title(f"SHAP Dependence - {feat}", fontsize=11)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIG_DEPENDENCE, bbox_inches="tight", dpi=110)
    plt.close()
    print(f"    Guardada: {FIG_DEPENDENCE.name}")

def grafico_waterfall(shap_values, X_test, y_test, caso_idx: int = 0):
    """
    Waterfall plot: explica una prediccion individual.
    Elegimos el caso con mayor error absoluto para ver donde falla.
    """
    print(f"  Generando waterfall plot para un caso concreto...")

    plt.figure(figsize=(11, 9))
    shap.plots.waterfall(shap_values[caso_idx], show=False, max_display=12)
    plt.title(f"SHAP Waterfall - Explicacion de una prediccion individual",
              fontsize=12, pad=15)
    plt.tight_layout()
    plt.savefig(FIG_WATERFALL, bbox_inches="tight", dpi=110)
    plt.close()
    print(f"    Guardada: {FIG_WATERFALL.name}")


def grafico_heatmap(shap_values, top_n: int = 15):
    """
    Heatmap de correlacion entre las top features SHAP.
    Muestra que features 'colaboran' o 'compiten' entre si.
    """
    print(f"  Generando heatmap de correlaciones SHAP...")

    # Top N features por importancia
    mean_abs = np.abs(shap_values.values).mean(axis=0)
    top_idx = np.argsort(mean_abs)[-top_n:][::-1]
    top_feats = [shap_values.feature_names[i] for i in top_idx]

    # Extraer SHAP de esas features
    shap_top = shap_values.values[:, top_idx]

    # Correlacion
    corr = np.corrcoef(shap_top.T)

    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        corr, xticklabels=top_feats, yticklabels=top_feats,
        cmap="coolwarm", center=0, vmin=-1, vmax=1,
        annot=True, fmt=".2f", annot_kws={"size": 7},
        cbar_kws={"label": "Correlacion de SHAP values"},
        ax=ax,
    )
    ax.set_title(f"Correlacion entre SHAP values de las top {top_n} features")
    plt.tight_layout()
    plt.savefig(FIG_HEATMAP, bbox_inches="tight", dpi=110)
    plt.close()
    print(f"    Guardada: {FIG_HEATMAP.name}")


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("SHAP - INTERPRETABILIDAD DEL MODELO XGBOOST")
    print("=" * 60)

    # 1. Cargar
    modelo, X_train, X_test, y_test, FEATURES = cargar_modelo_y_datos()

 

    # 2. Calcular SHAP
    explainer, shap_values = calcular_shap(modelo, X_train, X_test)

    # 3. Importancia global (top features)
    mean_abs_shap = np.abs(shap_values.values).mean(axis=0)
    importancias = pd.DataFrame({
        "feature": FEATURES,
        "mean_abs_shap": mean_abs_shap,
    }).sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)

    print("\n" + "=" * 60)
    print("TOP 20 FEATURES POR SHAP")
    print("=" * 60)
    print(importancias.head(20).to_string(index=False))

    # Top 3 features para dependence plots
    top3 = importancias.head(3)["feature"].tolist()
    print(f"\nTop 3 features: {top3}")

    # 4. Graficos
    print("\nGenerando graficos SHAP...")
    grafico_summary(shap_values)
    grafico_bar(shap_values)
    grafico_dependence(shap_values, top3)

    # Caso para waterfall: elegimos el que tenga mayor |residuo|
    y_pred = modelo.predict(X_test)
    residuos = np.abs(y_test - y_pred)
    caso_idx = int(np.argmax(residuos))
    print(f"\n  Caso seleccionado para waterfall:")
    print(f"    Indice: {caso_idx}")
    print(f"    Real: {y_test[caso_idx]:.0f}")
    print(f"    Pred: {y_pred[caso_idx]:.1f}")
    print(f"    |Residuo|: {residuos[caso_idx]:.1f}")

    grafico_waterfall(shap_values, X_test, y_test, caso_idx)
    grafico_heatmap(shap_values)

    # 5. Guardar SHAP values (con un formato reutilizable)
    print("\nGuardando SHAP values...")
    with open(SALIDA_SHAP, "wb") as f:
        pickle.dump({
            "shap_values": shap_values.values,
            "feature_names": FEATURES,
            "base_value": float(shap_values.base_values[0])
                              if hasattr(shap_values.base_values, "__len__")
                              else float(shap_values.base_values),
        }, f)
    print(f"  Guardado: {SALIDA_SHAP.name}")

    # Resumen
    print("\n" + "=" * 60)
    print("SHAP COMPLETADO")
    print("=" * 60)
    print(f"Features analizadas: {len(FEATURES)}")
    print(f"Casos SHAP: {shap_values.values.shape[0]}")
    print(f"Top feature: {importancias.iloc[0]['feature']} "
          f"(impacto medio: {importancias.iloc[0]['mean_abs_shap']:.3f})")


if __name__ == "__main__":
    main()