# analisis_serpavi_distrito.py
# Analisis descriptivo cruzando SERPAVI (alquiler) y Notariado (transacciones)
# a nivel de distrito de Barcelona.
#
# Entrada:
#   data/raw/serpavi/2026-03-09_bd_SERPAVI_2011-2024 - DEFINITIVO WEB.xlsx
#   data/processed/barcelona_barrio_mes_filtrado.csv
#
# Salidas:
#   reports/metricas/serpavi_distrito_correlacion.csv
#   reports/figuras/20_serpavi_vs_transacciones.png
#   reports/figuras/21_serpavi_evolucion.png

from pathlib import Path
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.utilidades.config import (
    DATA_RAW, DATA_PROCESSED, METRICAS_DIR, FIGURAS_DIR
)


SERPAVI_PATH = DATA_RAW / "serpavi" / "2026-03-09_bd_SERPAVI_2011-2024 - DEFINITIVO WEB.xlsx"
NOTARIADO_PATH = DATA_PROCESSED / "barcelona_barrio_mes_filtrado.csv"

SALIDA_METRICAS = METRICAS_DIR / "serpavi_distrito_correlacion.csv"
FIG_SCATTER = FIGURAS_DIR / "20_serpavi_vs_transacciones.png"
FIG_EVOLUCION = FIGURAS_DIR / "21_serpavi_evolucion.png"

# Codigos distrito (INE) - nombre
DISTRITOS = {
    801901: "Ciutat Vella",
    801902: "Eixample",
    801903: "Sants-Montjuïc",
    801904: "Les Corts",
    801905: "Sarrià-Sant Gervasi",
    801906: "Gràcia",
    801907: "Horta-Guinardó",
    801908: "Nou Barris",
    801909: "Sant Andreu",
    801910: "Sant Martí",
}

ANYO_ANALISIS = 2024


# ============================================================
# CARGA DE DATOS
# ============================================================
def cargar_serpavi(anyo: int) -> pd.DataFrame:
    """Carga SERPAVI y extrae el alquiler medio de un año concreto."""
    print(f"Cargando SERPAVI (año {anyo})...")

    df = pd.read_excel(SERPAVI_PATH, sheet_name="Distritos")

    # Filtrar Barcelona
    df = df[df["CUMUN"] == 8019].copy()

    # Codigo corto de año (2 digitos): 2024 -> 24
    sufijo = str(anyo)[-2:]

    # Columna de alquiler medio €/m²/mes (vivienda colectiva, mercado libre)
    col_alquiler = f"ALQM2_LV_M_VC_{sufijo}"
    col_alquiler_25 = f"ALQM2_LV_25_VC_{sufijo}"
    col_alquiler_75 = f"ALQM2_LV_75_VC_{sufijo}"
    col_testigos = f"BI_ALVHEPCO_TVC_{sufijo}"

    resultado = df[["CUDIS", col_alquiler, col_alquiler_25, col_alquiler_75, col_testigos]].copy()
    resultado.columns = ["CUDIS", "alquiler_m2", "alquiler_p25", "alquiler_p75", "num_testigos"]
    resultado["distrito"] = resultado["CUDIS"].map(DISTRITOS)

    print(f"  Distritos: {len(resultado)}")
    print(resultado[["distrito", "alquiler_m2", "num_testigos"]].to_string(index=False))

    return resultado


def cargar_transacciones(anyo: int) -> pd.DataFrame:
    """Carga nuestro dataset de transacciones y agrega por distrito."""
    print(f"\nCargando transacciones de {anyo}...")

    df = pd.read_csv(NOTARIADO_PATH, parse_dates=["fecha"])

    # Filtrar año
    df = df[df["Any"] == anyo].copy()

    # Agregar por distrito
    agg = df.groupby("Nom_Districte").agg(
        transacciones_totales=("total_transacciones", "sum"),
        transacciones_medias=("total_transacciones", "mean"),
        num_barrios=("Nom_Barri", "nunique"),
    ).reset_index()
    agg = agg.rename(columns={"Nom_Districte": "distrito"})

    print(f"  Distritos: {len(agg)}")
    print(agg.to_string(index=False))

    return agg


# ============================================================
# ANALISIS
# ============================================================
def cruzar_datos(serpavi: pd.DataFrame, trans: pd.DataFrame) -> pd.DataFrame:
    """Cruza los dos datasets por distrito."""
    print("\nCruzando datos por distrito...")

    df = pd.merge(serpavi, trans, on="distrito", how="inner")

    # Transacciones por 1000 testigos (o normalizado)
    df["transacciones_por_testigo"] = df["transacciones_totales"] / df["num_testigos"].replace(0, np.nan)

    print(f"  Filas finales: {len(df)}")
    print(df[["distrito", "alquiler_m2", "transacciones_totales", "num_barrios"]].to_string(index=False))

    return df


def calcular_correlaciones(df: pd.DataFrame) -> dict:
    """Calcula correlaciones Pearson y Spearman."""
    print("\nCalculando correlaciones...")

    x = df["alquiler_m2"].values
    y = df["transacciones_totales"].values

    # Pearson (lineal)
    pearson_r, pearson_p = stats.pearsonr(x, y)

    # Spearman (monotonica)
    spearman_r, spearman_p = stats.spearmanr(x, y)

    print(f"  Pearson:  r={pearson_r:.3f}, p={pearson_p:.4f}")
    print(f"  Spearman: r={spearman_r:.3f}, p={spearman_p:.4f}")

    return {
        "pearson_r": round(pearson_r, 4),
        "pearson_p": round(pearson_p, 4),
        "spearman_r": round(spearman_r, 4),
        "spearman_p": round(spearman_p, 4),
    }


# ============================================================
# VISUALIZACIONES
# ============================================================
def grafico_scatter(df: pd.DataFrame, correlaciones: dict):
    """Scatter alquiler vs transacciones."""
    print("\nGenerando scatter plot...")

    fig, ax = plt.subplots(figsize=(12, 7))

    # Scatter
    scatter = ax.scatter(
        df["alquiler_m2"], df["transacciones_totales"],
        s=df["num_barrios"] * 30,
        c=df["alquiler_m2"], cmap="viridis",
        alpha=0.8, edgecolors="black", linewidth=1.5,
    )

    # Anotar cada punto con el nombre del distrito
    for _, row in df.iterrows():
        ax.annotate(
            row["distrito"], (row["alquiler_m2"], row["transacciones_totales"]),
            xytext=(8, 5), textcoords="offset points", fontsize=9, alpha=0.85,
        )

    # Recta de regresion
    z = np.polyfit(df["alquiler_m2"], df["transacciones_totales"], 1)
    p = np.poly1d(z)
    x_sorted = np.sort(df["alquiler_m2"])
    ax.plot(x_sorted, p(x_sorted), "r--", alpha=0.6, linewidth=1.5,
            label=f"Regresion lineal")

    ax.set_title(
        f"SERPAVI vs Transacciones por distrito (Barcelona, {ANYO_ANALISIS})\n"
        f"Pearson r={correlaciones['pearson_r']:.3f} | "
        f"Spearman ρ={correlaciones['spearman_r']:.3f}",
        fontsize=13,
    )
    ax.set_xlabel("Precio medio alquiler (€/m²/mes) — SERPAVI")
    ax.set_ylabel(f"Transacciones totales {ANYO_ANALISIS}")
    ax.grid(True, alpha=0.3)
    ax.legend()

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Alquiler €/m²/mes")

    plt.tight_layout()
    plt.savefig(FIG_SCATTER, bbox_inches="tight", dpi=110)
    plt.close()
    print(f"  Figura guardada: {FIG_SCATTER.name}")


def grafico_evolucion(anyos: list = [2015, 2018, 2020, 2022, 2024]):
    """Evolucion del alquiler por distrito en varios años."""
    print(f"\nGenerando grafico de evolucion ({anyos})...")

    df = pd.read_excel(SERPAVI_PATH, sheet_name="Distritos")
    df = df[df["CUMUN"] == 8019].copy()
    df["distrito"] = df["CUDIS"].map(DISTRITOS)

    # Extraer alquiler medio para cada año
    filas = []
    for anyo in anyos:
        sufijo = str(anyo)[-2:]
        col = f"ALQM2_LV_M_VC_{sufijo}"
        if col in df.columns:
            for _, row in df.iterrows():
                filas.append({
                    "distrito": row["distrito"],
                    "anyo": anyo,
                    "alquiler_m2": row[col],
                })

    df_evol = pd.DataFrame(filas)

    fig, ax = plt.subplots(figsize=(13, 6))

    for distrito in sorted(df_evol["distrito"].unique()):
        data = df_evol[df_evol["distrito"] == distrito]
        ax.plot(data["anyo"], data["alquiler_m2"], marker="o", linewidth=2, label=distrito)

    ax.set_title(f"Evolucion del alquiler medio por distrito (Barcelona, {min(anyos)}-{max(anyos)})",
                 fontsize=13)
    ax.set_xlabel("Año")
    ax.set_ylabel("Alquiler €/m²/mes")
    ax.legend(title="Distrito", loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIG_EVOLUCION, bbox_inches="tight", dpi=110)
    plt.close()
    print(f"  Figura guardada: {FIG_EVOLUCION.name}")


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print(f"ANALISIS SERPAVI vs TRANSACCIONES ({ANYO_ANALISIS})")
    print("=" * 60)

    # 1. Cargar
    serpavi = cargar_serpavi(ANYO_ANALISIS)
    trans = cargar_transacciones(ANYO_ANALISIS)

    # 2. Cruzar
    df = cruzar_datos(serpavi, trans)

    # 3. Correlaciones
    corr = calcular_correlaciones(df)

    # 4. Guardar metricas
    df_out = df.copy()
    for k, v in corr.items():
        df_out[k] = v
    df_out.to_csv(SALIDA_METRICAS, index=False)
    print(f"\n  Metricas guardadas: {SALIDA_METRICAS.name}")

    # 5. Graficos
    grafico_scatter(df, corr)
    grafico_evolucion()

    # 6. Conclusiones
    print("\n" + "=" * 60)
    print("CONCLUSIONES")
    print("=" * 60)
    if corr["pearson_r"] > 0.5:
        print("  Correlacion POSITIVA FUERTE: distritos con alquiler mas alto")
        print("  tienden a tener mas transacciones.")
    elif corr["pearson_r"] > 0.2:
        print("  Correlacion POSITIVA MODERADA.")
    elif corr["pearson_r"] > -0.2:
        print("  Correlacion DEBIL o NULA.")
    elif corr["pearson_r"] > -0.5:
        print("  Correlacion NEGATIVA MODERADA.")
    else:
        print("  Correlacion NEGATIVA FUERTE: distritos con alquiler mas alto")
        print("  tienden a tener MENOS transacciones.")

    print(f"\n  Alquiler mas alto: {df.loc[df['alquiler_m2'].idxmax(), 'distrito']} "
          f"({df['alquiler_m2'].max():.2f} €/m²/mes)")
    print(f"  Alquiler mas bajo: {df.loc[df['alquiler_m2'].idxmin(), 'distrito']} "
          f"({df['alquiler_m2'].min():.2f} €/m²/mes)")
    print(f"  Mas transacciones: {df.loc[df['transacciones_totales'].idxmax(), 'distrito']} "
          f"({df['transacciones_totales'].max():,})")
    print(f"  Menos transacciones: {df.loc[df['transacciones_totales'].idxmin(), 'distrito']} "
          f"({df['transacciones_totales'].min():,})")


if __name__ == "__main__":
    main()