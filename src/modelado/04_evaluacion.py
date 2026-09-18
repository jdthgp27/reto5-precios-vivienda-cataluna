# 04_evaluacion.py
# Evaluacion profunda del modelo XGBoost final.
#
# Entrada:
#   data/processed/predicciones_xgboost.csv
#   data/processed/test.csv
#
# Salidas:
#   reports/figuras/12_analisis_residuos.png
#   reports/figuras/13_residuos_por_barrio.png
#   reports/figuras/14_residuos_por_mes.png
#   reports/metricas/evaluacion_por_barrio.csv
#   reports/metricas/evaluacion_por_mes.csv
#   reports/metricas/evaluacion_por_magnitud.csv

from pathlib import Path
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.utilidades.config import (
    DATA_PROCESSED, METRICAS_DIR, FIGURAS_DIR
)


PRED_PATH = DATA_PROCESSED / "predicciones_xgboost.csv"
TEST_PATH = DATA_PROCESSED / "test.csv"

FIG_RESIDUOS = FIGURAS_DIR / "12_analisis_residuos.png"
FIG_BARRIO = FIGURAS_DIR / "13_residuos_por_barrio.png"
FIG_MES = FIGURAS_DIR / "14_residuos_por_mes.png"

SALIDA_BARRIO = METRICAS_DIR / "evaluacion_por_barrio.csv"
SALIDA_MES = METRICAS_DIR / "evaluacion_por_mes.csv"
SALIDA_MAGNITUD = METRICAS_DIR / "evaluacion_por_magnitud.csv"

TARGET = "total_transacciones"
PRED = "prediccion"
RESID = "residuo"


# ============================================================
# UTILIDADES
# ============================================================
def metricas_grupo(df: pd.DataFrame, col_grupo) -> pd.DataFrame:
    """Calcula RMSE, MAE, MAPE, sesgo por grupo."""
    def agg(g):
        y = g[TARGET].values
        p = g[PRED].values
        r = g[RESID].values

        rmse = np.sqrt(np.mean(r ** 2))
        mae = np.mean(np.abs(r))
        sesgo = np.mean(r)
        mask = y > 0
        if mask.sum() > 0:
            mape = np.mean(np.abs(r[mask] / y[mask])) * 100
        else:
            mape = np.nan

        return pd.Series({
            "n": len(g),
            "rmse": round(rmse, 3),
            "mae": round(mae, 3),
            "sesgo": round(sesgo, 3),
            "mape": round(mape, 2) if not np.isnan(mape) else None,
            "real_medio": round(y.mean(), 2),
            "pred_medio": round(p.mean(), 2),
        })

    return df.groupby(col_grupo).apply(agg).reset_index()


# ============================================================
# BLOQUE 1: DISTRIBUCION DE RESIDUOS
# ============================================================
def bloque1_distribucion_residuos(df: pd.DataFrame):
    print("\n=== BLOQUE 1: Distribucion de residuos ===")

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Histograma
    axes[0].hist(df[RESID], bins=50, color="#2E86AB", edgecolor="white")
    axes[0].axvline(0, color="red", linestyle="--", linewidth=1.5)
    axes[0].axvline(df[RESID].mean(), color="green", linestyle="--",
                    linewidth=1.5, label=f"Media = {df[RESID].mean():.2f}")
    axes[0].set_title("Distribucion de residuos")
    axes[0].set_xlabel("Residuo (real - prediccion)")
    axes[0].set_ylabel("Frecuencia")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # QQ-plot
    from scipy import stats
    stats.probplot(df[RESID], dist="norm", plot=axes[1])
    axes[1].set_title("Q-Q plot de residuos vs normal")
    axes[1].grid(True, alpha=0.3)

    # Residuos vs prediccion
    axes[2].scatter(df[PRED], df[RESID], alpha=0.3, s=15, color="#F18F01")
    axes[2].axhline(0, color="red", linestyle="--", linewidth=1.5)
    axes[2].set_title("Residuos vs Prediccion")
    axes[2].set_xlabel("Prediccion")
    axes[2].set_ylabel("Residuo")
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIG_RESIDUOS, bbox_inches="tight", dpi=110)
    plt.close()
    print(f"  Figura guardada: {FIG_RESIDUOS.name}")

    # Estadisticas
    print(f"  Media residuo: {df[RESID].mean():.3f}")
    print(f"  Std residuo:   {df[RESID].std():.3f}")
    print(f"  Asimetria:     {df[RESID].skew():.3f}")
    print(f"  Kurtosis:      {df[RESID].kurtosis():.3f}")


# ============================================================
# BLOQUE 2: RESIDUOS POR BARRIO
# ============================================================
def bloque2_por_barrio(df: pd.DataFrame):
    print("\n=== BLOQUE 2: Residuos por barrio ===")

    metricas = metricas_grupo(df, "Nom_Barri")
    metricas = metricas.sort_values("mape", ascending=False)

    # Top 15 peores
    top15_peores = metricas.head(15)
    # Top 15 mejores
    top15_mejores = metricas.tail(15).sort_values("mape", ascending=False)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    sns.barplot(data=top15_peores, y="Nom_Barri", x="mape",
                hue="Nom_Barri", palette="Reds_r", legend=False, ax=axes[0])
    axes[0].set_title("Top 15 barrios con mayor MAPE")
    axes[0].set_xlabel("MAPE (%)")
    axes[0].set_ylabel("")
    axes[0].grid(True, alpha=0.3, axis="x")

    sns.barplot(data=top15_mejores, y="Nom_Barri", x="mape",
                hue="Nom_Barri", palette="Greens_r", legend=False, ax=axes[1])
    axes[1].set_title("Top 15 barrios con menor MAPE")
    axes[1].set_xlabel("MAPE (%)")
    axes[1].set_ylabel("")
    axes[1].grid(True, alpha=0.3, axis="x")

    plt.tight_layout()
    plt.savefig(FIG_BARRIO, bbox_inches="tight", dpi=110)
    plt.close()
    print(f"  Figura guardada: {FIG_BARRIO.name}")

    metricas.to_csv(SALIDA_BARRIO, index=False)
    print(f"  Metricas por barrio guardadas")

    print(f"\n  Barrio con PEOR MAPE: {metricas.iloc[0]['Nom_Barri']} "
          f"({metricas.iloc[0]['mape']:.1f}%)")
    print(f"  Barrio con MEJOR MAPE: {metricas.iloc[-1]['Nom_Barri']} "
          f"({metricas.iloc[-1]['mape']:.1f}%)")


# ============================================================
# BLOQUE 3: RESIDUOS POR MES
# ============================================================
def bloque3_por_mes(df: pd.DataFrame):
    print("\n=== BLOQUE 3: Residuos por mes ===")

    metricas = metricas_grupo(df, "Mes")
    metricas = metricas.sort_values("Mes")

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # MAPE por mes
    axes[0].bar(metricas["Mes"], metricas["mape"],
                color="#2E86AB", edgecolor="white")
    axes[0].set_title("MAPE por mes")
    axes[0].set_xlabel("Mes")
    axes[0].set_ylabel("MAPE (%)")
    axes[0].set_xticks(range(1, 13))
    axes[0].grid(True, alpha=0.3, axis="y")

    # Sesgo por mes
    colors = ["red" if s < 0 else "green" for s in metricas["sesgo"]]
    axes[1].bar(metricas["Mes"], metricas["sesgo"],
                color=colors, edgecolor="white")
    axes[1].axhline(0, color="black", linewidth=1)
    axes[1].set_title("Sesgo por mes (positivo: infravaloramos)")
    axes[1].set_xlabel("Mes")
    axes[1].set_ylabel("Sesgo (real - pred)")
    axes[1].set_xticks(range(1, 13))
    axes[1].grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(FIG_MES, bbox_inches="tight", dpi=110)
    plt.close()
    print(f"  Figura guardada: {FIG_MES.name}")

    metricas.to_csv(SALIDA_MES, index=False)
    print(f"  Metricas por mes guardadas")

    peor = metricas.loc[metricas["mape"].idxmax()]
    mejor = metricas.loc[metricas["mape"].idxmin()]
    print(f"\n  Mes con PEOR MAPE: {int(peor['Mes'])} ({peor['mape']:.1f}%)")
    print(f"  Mes con MEJOR MAPE: {int(mejor['Mes'])} ({mejor['mape']:.1f}%)")


# ============================================================
# BLOQUE 4: RESIDUOS POR MAGNITUD
# ============================================================
def bloque4_por_magnitud(df: pd.DataFrame):
    print("\n=== BLOQUE 4: Residuos por magnitud del target ===")

    # Crear buckets por magnitud
    bins = [0, 5, 15, 30, 60, 100, 1000]
    labels = ["0-5", "5-15", "15-30", "30-60", "60-100", "100+"]
    df = df.copy()
    df["bucket"] = pd.cut(df[TARGET], bins=bins, labels=labels, right=False)

    metricas = metricas_grupo(df, "bucket")
    print("\n  Metricas por rango de magnitud:")
    print(metricas.to_string(index=False))

    metricas.to_csv(SALIDA_MAGNITUD, index=False)
    print(f"\n  Metricas por magnitud guardadas")

    # Analisis
    print("\n  Analisis:")
    for _, row in metricas.iterrows():
        sesgo_txt = "sobreestima" if row["sesgo"] < 0 else "subestima"
        print(f"    {row['bucket']:>8}: MAPE={row['mape']:.1f}%, sesgo={row['sesgo']:+.2f} ({sesgo_txt})")


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("EVALUACION DETALLADA DEL MODELO XGBOOST")
    print("=" * 60)

    # Cargar
    print("\nCargando datos...")
    df = pd.read_csv(PRED_PATH)
    print(f"  Predicciones: {len(df):,} filas")

    # Resumen global
    print("\n" + "=" * 60)
    print("METRICAS GLOBALES")
    print("=" * 60)
    rmse = np.sqrt(np.mean(df[RESID] ** 2))
    mae = np.mean(np.abs(df[RESID]))
    print(f"  RMSE: {rmse:.3f}")
    print(f"  MAE:  {mae:.3f}")
    print(f"  Media residuo: {df[RESID].mean():+.3f}")

    # Bloques
    bloque1_distribucion_residuos(df)
    bloque2_por_barrio(df)
    bloque3_por_mes(df)
    bloque4_por_magnitud(df)

    print("\n" + "=" * 60)
    print("EVALUACION COMPLETADA")
    print("=" * 60)


if __name__ == "__main__":
    main()