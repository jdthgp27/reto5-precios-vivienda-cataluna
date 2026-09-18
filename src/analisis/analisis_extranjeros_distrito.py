# analisis_extranjeros_distrito.py
# Analisis descriptivo: extranjeros, alquiler y compraventa por distrito.
#
# Este script combina datos de 3 fuentes externas (cargadas manualmente)
# con el dataset del Notariado para generar 5 graficos de barras.
#
# Fuentes externas (hardcoded a partir de informes publicos):
#   - Padron Municipal 2024 (Ayuntamiento de Barcelona)
#   - Institut Metropoli 2024 (regimen de tenencia por origen)
#   - Ayuntamiento de Barcelona 2025 (compradores extranjeros)
#
# Entrada:
#   data/processed/barcelona_barrio_mes_filtrado.csv
#   data/raw/serpavi/2026-03-09_bd_SERPAVI_2011-2024 - DEFINITIVO WEB.xlsx
#
# Salidas:
#   reports/figuras/22_alquiler_por_distrito.png
#   reports/figuras/23_compraventas_por_distrito.png
#   reports/figuras/24_compradores_extranjeros.png
#   reports/figuras/25_poblacion_extranjera.png
#   reports/figuras/26_inquilinos_extranjeros_estimado.png
#   reports/metricas/analisis_extranjeros_distrito.csv

from pathlib import Path
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.utilidades.config import (
    DATA_RAW, DATA_PROCESSED, METRICAS_DIR, FIGURAS_DIR
)


SERPAVI_PATH = DATA_RAW / "serpavi" / "2026-03-09_bd_SERPAVI_2011-2024 - DEFINITIVO WEB.xlsx"
NOTARIADO_PATH = DATA_PROCESSED / "barcelona_barrio_mes_filtrado.csv"

SALIDA_CSV = METRICAS_DIR / "analisis_extranjeros_distrito.csv"

ANYO = 2024

# Tasa de alquiler entre poblacion extranjera (Institut Metropoli 2024)
TASA_ALQUILER_EXTRANJEROS = 0.705


# ============================================================
# DATOS EXTERNOS (hardcoded de informes publicos)
# ============================================================

# Codigos distrito INE -> nombre
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

# % de compradores extranjeros por distrito (Ayuntamiento BCN 2025)
# Fuente: datos publicos de la ciudad de Barcelona 2025
COMPRADORES_EXTRANJEROS = {
    "Ciutat Vella": 42.6,
    "Eixample": 27.8,
    "Sants-Montjuïc": 26.0,      # estimado, no confirmado
    "Les Corts": 12.9,
    "Sarrià-Sant Gervasi": 11.5,
    "Gràcia": 22.0,              # estimado
    "Horta-Guinardó": 24.0,      # estimado
    "Nou Barris": 28.0,          # estimado
    "Sant Andreu": 25.0,         # estimado
    "Sant Martí": 30.9,
}

# % de poblacion extranjera por distrito (Padron 2024)
# Fuente: Ayuntamiento de Barcelona
POBLACION_EXTRANJERA = {
    "Ciutat Vella": 63.7,
    "Eixample": 30.9,
    "Sants-Montjuïc": 31.7,
    "Les Corts": 18.1,
    "Sarrià-Sant Gervasi": 15.0,   # estimado
    "Gràcia": 22.0,                # estimado
    "Horta-Guinardó": 24.0,        # estimado
    "Nou Barris": 32.0,
    "Sant Andreu": 22.0,           # estimado
    "Sant Martí": 27.7,
}


# ============================================================
# CARGA DE DATOS
# ============================================================
def cargar_alquiler_2024() -> pd.DataFrame:
    """Carga SERPAVI y extrae alquiler medio 2024 por distrito."""
    print("Cargando alquiler SERPAVI...")
    df = pd.read_excel(SERPAVI_PATH, sheet_name="Distritos")
    df = df[df["CUMUN"] == 8019].copy()

    sufijo = str(ANYO)[-2:]
    col_alquiler = f"ALQM2_LV_M_VC_{sufijo}"

    resultado = df[["CUDIS", col_alquiler]].copy()
    resultado.columns = ["CUDIS", "alquiler_m2"]
    resultado["distrito"] = resultado["CUDIS"].map(DISTRITOS)
    return resultado[["distrito", "alquiler_m2"]]


def cargar_compraventas_2024() -> pd.DataFrame:
    """Carga transacciones del Notariado y agrega por distrito."""
    print("Cargando compraventas del Notariado...")
    df = pd.read_csv(NOTARIADO_PATH, parse_dates=["fecha"])
    df = df[df["Any"] == ANYO].copy()

    agg = df.groupby("Nom_Districte")["total_transacciones"].sum().reset_index()
    agg.columns = ["distrito", "compraventas"]
    return agg


def construir_dataset() -> pd.DataFrame:
    """Combina todas las fuentes en un unico DataFrame."""
    print("\nConstruyendo dataset consolidado...")

    df_alq = cargar_alquiler_2024()
    df_comp = cargar_compraventas_2024()

    # Merge
    df = df_alq.merge(df_comp, on="distrito", how="outer")

    # Anadir datos externos
    df["compradores_extranjeros_pct"] = df["distrito"].map(COMPRADORES_EXTRANJEROS)
    df["poblacion_extranjera_pct"] = df["distrito"].map(POBLACION_EXTRANJERA)

    # ESTIMACION: % inquilinos extranjeros
    df["inquilinos_extranjeros_estimado"] = (
        df["poblacion_extranjera_pct"] * TASA_ALQUILER_EXTRANJEROS
    )

    df = df.sort_values("alquiler_m2", ascending=False).reset_index(drop=True)
    print(f"  Filas: {len(df)}")
    print(df.to_string(index=False))
    return df


# ============================================================
# GRAFICOS DE BARRAS
# ============================================================
def grafico_1_alquiler(df: pd.DataFrame):
    """Grafico 1: Precio de alquiler por distrito."""
    print("\n  Generando grafico 1: alquiler por distrito...")

    fig, ax = plt.subplots(figsize=(12, 6))
    df_sorted = df.sort_values("alquiler_m2", ascending=True)

    sns.barplot(data=df_sorted, y="distrito", x="alquiler_m2",
                hue="distrito", palette="viridis", legend=False, ax=ax)

    ax.set_title(f"Precio medio del alquiler por distrito (€/m²/mes, {ANYO})",
                 fontsize=13, pad=15)
    ax.set_xlabel("€/m²/mes")
    ax.set_ylabel("")
    ax.grid(True, alpha=0.3, axis="x")

    # Anotar valores
    for i, v in enumerate(df_sorted["alquiler_m2"]):
        ax.text(v + 0.1, i, f"{v:.2f}", va="center", fontsize=9)

    plt.tight_layout()
    plt.savefig(FIGURAS_DIR / "22_alquiler_por_distrito.png", bbox_inches="tight", dpi=110)
    plt.close()
    print("    Guardada: 22_alquiler_por_distrito.png")


def grafico_2_compraventas(df: pd.DataFrame):
    """Grafico 2: Compraventas por distrito."""
    print("  Generando grafico 2: compraventas por distrito...")

    fig, ax = plt.subplots(figsize=(12, 6))
    df_sorted = df.sort_values("compraventas", ascending=True)

    sns.barplot(data=df_sorted, y="distrito", x="compraventas",
                hue="distrito", palette="mako", legend=False, ax=ax)

    ax.set_title(f"Compraventas totales por distrito ({ANYO})",
                 fontsize=13, pad=15)
    ax.set_xlabel("Transacciones")
    ax.set_ylabel("")
    ax.grid(True, alpha=0.3, axis="x")

    for i, v in enumerate(df_sorted["compraventas"]):
        ax.text(v + 30, i, f"{int(v):,}", va="center", fontsize=9)

    plt.tight_layout()
    plt.savefig(FIGURAS_DIR / "23_compraventas_por_distrito.png", bbox_inches="tight", dpi=110)
    plt.close()
    print("    Guardada: 23_compraventas_por_distrito.png")


def grafico_3_compradores(df: pd.DataFrame):
    """Grafico 3: % compradores extranjeros por distrito."""
    print("  Generando grafico 3: compradores extranjeros...")

    fig, ax = plt.subplots(figsize=(12, 6))
    df_sorted = df.sort_values("compradores_extranjeros_pct", ascending=True)

    # Color: rojo si > media, azul si < media
    media = df["compradores_extranjeros_pct"].mean()
    colors = ["#D62828" if v > media else "#2E86AB"
              for v in df_sorted["compradores_extranjeros_pct"]]

    ax.barh(df_sorted["distrito"], df_sorted["compradores_extranjeros_pct"],
            color=colors, edgecolor="white")

    # Linea de media
    ax.axvline(media, color="black", linestyle="--", linewidth=1.5,
               label=f"Media Barcelona ({media:.1f}%)")

    ax.set_title(f"% de compradores extranjeros por distrito (BCN, 2025)",
                 fontsize=13, pad=15)
    ax.set_xlabel("% compradores extranjeros")
    ax.set_ylabel("")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3, axis="x")

    for i, v in enumerate(df_sorted["compradores_extranjeros_pct"]):
        ax.text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=9)

    plt.tight_layout()
    plt.savefig(FIGURAS_DIR / "24_compradores_extranjeros.png", bbox_inches="tight", dpi=110)
    plt.close()
    print("    Guardada: 24_compradores_extranjeros.png")


def grafico_4_poblacion(df: pd.DataFrame):
    """Grafico 4: % poblacion extranjera por distrito."""
    print("  Generando grafico 4: poblacion extranjera...")

    fig, ax = plt.subplots(figsize=(12, 6))
    df_sorted = df.sort_values("poblacion_extranjera_pct", ascending=True)

    sns.barplot(data=df_sorted, y="distrito", x="poblacion_extranjera_pct",
                hue="distrito", palette="rocket_r", legend=False, ax=ax)

    ax.set_title(f"% de poblacion extranjera por distrito (Padron {ANYO})",
                 fontsize=13, pad=15)
    ax.set_xlabel("% poblacion extranjera")
    ax.set_ylabel("")
    ax.grid(True, alpha=0.3, axis="x")

    for i, v in enumerate(df_sorted["poblacion_extranjera_pct"]):
        ax.text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=9)

    plt.tight_layout()
    plt.savefig(FIGURAS_DIR / "25_poblacion_extranjera.png", bbox_inches="tight", dpi=110)
    plt.close()
    print("    Guardada: 25_poblacion_extranjera.png")


def grafico_5_inquilinos_estimado(df: pd.DataFrame):
    """Grafico 5: Estimacion % inquilinos extranjeros."""
    print("  Generando grafico 5: inquilinos extranjeros (ESTIMADO)...")

    fig, ax = plt.subplots(figsize=(12, 6))
    df_sorted = df.sort_values("inquilinos_extranjeros_estimado", ascending=True)

    sns.barplot(data=df_sorted, y="distrito", x="inquilinos_extranjeros_estimado",
                hue="distrito", palette="flare", legend=False, ax=ax)

    ax.set_title(
        f"ESTIMACION: % de inquilinos extranjeros por distrito\n"
        f"Formula: (% poblacion extranjera) x {TASA_ALQUILER_EXTRANJEROS*100:.1f}%",
        fontsize=12, pad=15,
    )
    ax.set_xlabel("% estimado de inquilinos extranjeros")
    ax.set_ylabel("")
    ax.grid(True, alpha=0.3, axis="x")

    for i, v in enumerate(df_sorted["inquilinos_extranjeros_estimado"]):
        ax.text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=9)

    # Nota metodologica
    fig.text(0.5, -0.02,
             "Estimacion basada en: Padron Municipal 2024 + Institut Metropoli 2024. "
             "Supuesto: la tasa de alquiler entre extranjeros es constante entre distritos.",
             ha="center", fontsize=8, style="italic", color="gray")

    plt.tight_layout()
    plt.savefig(FIGURAS_DIR / "26_inquilinos_extranjeros_estimado.png",
                bbox_inches="tight", dpi=110)
    plt.close()
    print("    Guardada: 26_inquilinos_extranjeros_estimado.png")


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("ANALISIS EXTRANJEROS Y VIVIENDA POR DISTRITO")
    print("=" * 60)

    # Construir dataset
    df = construir_dataset()

    # Guardar CSV
    METRICAS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA_CSV, index=False)
    print(f"\n  Dataset guardado: {SALIDA_CSV.name}")

    # Generar los 5 graficos
    print("\nGenerando graficos...")
    grafico_1_alquiler(df)
    grafico_2_compraventas(df)
    grafico_3_compradores(df)
    grafico_4_poblacion(df)
    grafico_5_inquilinos_estimado(df)

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"\n  Distrito con alquiler mas alto: {df.loc[df['alquiler_m2'].idxmax(), 'distrito']}")
    print(f"  Distrito con mas compraventas:  {df.loc[df['compraventas'].idxmax(), 'distrito']}")
    print(f"  Distrito con mas compradores extranjeros: {df.loc[df['compradores_extranjeros_pct'].idxmax(), 'distrito']}")
    print(f"  Distrito con mas poblacion extranjera: {df.loc[df['poblacion_extranjera_pct'].idxmax(), 'distrito']}")
    print(f"  Distrito con mas inquilinos extranjeros (estimado): {df.loc[df['inquilinos_extranjeros_estimado'].idxmax(), 'distrito']}")

    print("\n" + "=" * 60)
    print("ANALISIS COMPLETADO")
    print("=" * 60)
    print(f"\n  Figuras guardadas en: {FIGURAS_DIR}")


if __name__ == "__main__":
    main()