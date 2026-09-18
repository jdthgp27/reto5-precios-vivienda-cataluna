# eda_barcelona.py
# Analisis Exploratorio de Datos (EDA) del mercado inmobiliario
# de Barcelona a partir de los datos del Notariado.
#
# Entrada:
#   data/processed/barcelona_barrio_mes_filtrado.csv
#   data/processed/barcelona_barrio_mes_tipologia_filtrado.csv
#
# Salidas:
#   reports/figuras/*.png
#   Reporte de estadisticas por consola

from pathlib import Path
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.utilidades.config import DATA_PROCESSED, FIGURAS_DIR


# ============================================================
# CONFIGURACION
# ============================================================
ARCHIVO_VISTA1 = DATA_PROCESSED / "barcelona_barrio_mes_filtrado.csv"
ARCHIVO_VISTA2 = DATA_PROCESSED / "barcelona_barrio_mes_tipologia_filtrado.csv"

# Estilo global
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (13, 6)
plt.rcParams["figure.dpi"] = 110
plt.rcParams["font.size"] = 11
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.titleweight"] = "bold"


# ============================================================
# UTILIDADES
# ============================================================
def guardar_figura(nombre: str):
    """Guarda la figura actual en reports/figuras/."""
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)
    ruta = FIGURAS_DIR / nombre
    plt.savefig(ruta, bbox_inches="tight", dpi=110)
    print(f"  Guardada: {ruta.name}")
    plt.close()


# ============================================================
# BLOQUE 1: SERIE TEMPORAL GLOBAL
# ============================================================
def bloque1_serie_temporal(df: pd.DataFrame):
    print("\n=== BLOQUE 1: Serie temporal global ===")

    # Agregar por fecha
    serie = df.groupby("fecha")["total_transacciones"].sum().reset_index()

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(serie["fecha"], serie["total_transacciones"],
            color="#2E86AB", linewidth=1.8, label="Transacciones mensuales")

    # Media movil 12 meses
    serie["media_movil_12m"] = serie["total_transacciones"].rolling(12).mean()
    ax.plot(serie["fecha"], serie["media_movil_12m"],
            color="#D62828", linewidth=2.5, linestyle="--",
            label="Media movil 12 meses")

    # Marcar COVID (marzo 2020 - junio 2020)
    ax.axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2020-06-30"),
               alpha=0.20, color="red", label="Periodo COVID (mar-jun 2020)")

    # Marcar inicio 2022 (subida post-pandemia)
    ax.axvline(pd.Timestamp("2022-01-01"), color="green",
               linestyle=":", alpha=0.6, label="Inicio 2022")

    ax.set_title("Evolucion mensual de compraventas en Barcelona (2012-2025)")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Numero de transacciones")
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, alpha=0.3)

    guardar_figura("01_serie_temporal_global.png")

    # Estadisticas
    print(f"  Total transacciones 2012-2025: {serie['total_transacciones'].sum():,}")
    print(f"  Mes con mas transacciones: {serie.loc[serie['total_transacciones'].idxmax(), 'fecha'].date()} "
          f"({serie['total_transacciones'].max():,})")
    print(f"  Mes con menos transacciones: {serie.loc[serie['total_transacciones'].idxmin(), 'fecha'].date()} "
          f"({serie['total_transacciones'].min():,})")


# ============================================================
# BLOQUE 2: ESTACIONALIDAD
# ============================================================
def bloque2_estacionalidad(df: pd.DataFrame):
    print("\n=== BLOQUE 2: Estacionalidad ===")

    meses_nombre = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                    "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

    # Agregar por año y mes (Barcelona total)
    agg = df.groupby(["Any", "Mes"])["total_transacciones"].sum().reset_index()
    agg["Mes_nombre"] = agg["Mes"].map(lambda m: meses_nombre[m - 1])

    # --- Boxplot por mes ---
    fig, ax = plt.subplots(figsize=(13, 6))
    sns.boxplot(data=agg, x="Mes_nombre", y="total_transacciones",
                order=meses_nombre, palette="viridis", ax=ax)
    ax.set_title("Estacionalidad mensual de compraventas en Barcelona (2012-2025)")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Total transacciones (todos los barrios)")
    ax.grid(True, alpha=0.3, axis="y")
    guardar_figura("02_boxplot_estacionalidad.png")

    # --- Heatmap anio x mes ---
    pivot = agg.pivot_table(index="Any", columns="Mes",
                            values="total_transacciones", aggfunc="sum")

    fig, ax = plt.subplots(figsize=(14, 7))
    sns.heatmap(pivot, cmap="coolwarm", annot=True, fmt=".0f",
                linewidths=0.5, cbar_kws={"label": "Transacciones"}, ax=ax)
    ax.set_title("Heatmap de transacciones por anio y mes (Barcelona)")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Anio")
    guardar_figura("03_heatmap_anio_mes.png")

    # Estadisticas
    top_mes = agg.groupby("Mes_nombre")["total_transacciones"].mean().idxmax()
    bottom_mes = agg.groupby("Mes_nombre")["total_transacciones"].mean().idxmin()
    print(f"  Mes con mas actividad media: {top_mes}")
    print(f"  Mes con menos actividad media: {bottom_mes}")


# ============================================================
# BLOQUE 3: RANKING DE BARRIOS
# ============================================================
def bloque3_ranking_barrios(df: pd.DataFrame):
    print("\n=== BLOQUE 3: Ranking de barrios ===")

    ranking = (df.groupby("Nom_Barri")["total_transacciones"]
               .sum().sort_values(ascending=False).reset_index())

    # Top 15 y Bottom 15
    top15 = ranking.head(15)
    bottom15 = ranking.tail(15).sort_values("total_transacciones")

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Top 15
    sns.barplot(data=top15, y="Nom_Barri", x="total_transacciones",
                palette="viridis", ax=axes[0])
    axes[0].set_title("Top 15 barrios por transacciones totales")
    axes[0].set_xlabel("Total transacciones (2012-2025)")
    axes[0].set_ylabel("")
    axes[0].grid(True, alpha=0.3, axis="x")

    # Bottom 15
    sns.barplot(data=bottom15, y="Nom_Barri", x="total_transacciones",
                palette="coolwarm_r", ax=axes[1])
    axes[1].set_title("Bottom 15 barrios por transacciones totales")
    axes[1].set_xlabel("Total transacciones (2012-2025)")
    axes[1].set_ylabel("")
    axes[1].grid(True, alpha=0.3, axis="x")

    plt.tight_layout()
    guardar_figura("04_ranking_barrios.png")

    print(f"  Barrio top: {ranking.iloc[0]['Nom_Barri']} ({ranking.iloc[0]['total_transacciones']:,})")
    print(f"  Barrio bottom: {ranking.iloc[-1]['Nom_Barri']} ({ranking.iloc[-1]['total_transacciones']:,})")


# ============================================================
# BLOQUE 4: EVOLUCION POR TIPOLOGIA
# ============================================================
def bloque4_tipologia(df_tipo: pd.DataFrame):
    print("\n=== BLOQUE 4: Evolucion por tipologia ===")

    # Agregar por anio y tipologia
    agg = df_tipo.groupby(["Any", "Tipologia_Us_Desc"])["num_transacciones"].sum().reset_index()

    # --- Stacked area (proporciones) ---
    pivot_pct = agg.pivot_table(index="Any", columns="Tipologia_Us_Desc",
                                 values="num_transacciones", aggfunc="sum").fillna(0)
    pivot_pct_norm = pivot_pct.div(pivot_pct.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(13, 6))
    pivot_pct_norm.plot.area(ax=ax, cmap="viridis", alpha=0.85)
    ax.set_title("Evolucion porcentual de tipologias de compraventa (Barcelona)")
    ax.set_xlabel("Anio")
    ax.set_ylabel("Porcentaje del total (%)")
    ax.set_ylim(0, 100)
    ax.legend(title="Tipologia", loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=9)
    ax.grid(True, alpha=0.3)
    guardar_figura("05_tipologia_porcentual.png")

    # --- Lineas absolutas (sin Residencial para ver el detalle) ---
    agg_sin_res = agg[agg["Tipologia_Us_Desc"] != "Residencial"]
    pivot_abs = agg_sin_res.pivot_table(index="Any", columns="Tipologia_Us_Desc",
                                          values="num_transacciones", aggfunc="sum").fillna(0)

    fig, ax = plt.subplots(figsize=(13, 6))
    pivot_abs.plot(ax=ax, marker="o", linewidth=2, cmap="viridis")
    ax.set_title("Evolucion absoluta de tipologias no residenciales (Barcelona)")
    ax.set_xlabel("Anio")
    ax.set_ylabel("Numero de transacciones")
    ax.legend(title="Tipologia", loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=9)
    ax.grid(True, alpha=0.3)
    guardar_figura("06_tipologia_absoluta_no_residencial.png")


# ============================================================
# BLOQUE 5: HEATMAP BARRIO x ANIO
# ============================================================
def bloque5_heatmap_barrio_anio(df: pd.DataFrame):
    print("\n=== BLOQUE 5: Heatmap barrio x anio ===")

    # Total por barrio y anio
    pivot = df.pivot_table(index="Nom_Barri", columns="Any",
                           values="total_transacciones", aggfunc="sum").fillna(0)

    # Normalizar por barrio (indice 2012 = 100) para ver crecimiento relativo
    pivot_norm = pivot.div(pivot[2012].replace(0, np.nan), axis=0) * 100
    pivot_norm = pivot_norm.dropna()

    fig, ax = plt.subplots(figsize=(16, 14))
    sns.heatmap(pivot_norm, cmap="coolwarm", center=100, linewidths=0.3,
                cbar_kws={"label": "Indice (2012 = 100)"}, ax=ax)
    ax.set_title("Indice de actividad por barrio (2012 = 100)")
    ax.set_xlabel("Anio")
    ax.set_ylabel("Barrio")
    plt.yticks(fontsize=7)
    guardar_figura("07_heatmap_barrio_anio.png")


# ============================================================
# BLOQUE 6: DISTRIBUCION DEL TARGET
# ============================================================
def bloque6_distribucion(df: pd.DataFrame):
    print("\n=== BLOQUE 6: Distribucion del target ===")

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # Histograma
    axes[0].hist(df["total_transacciones"], bins=50,
                 color="#2E86AB", edgecolor="white")
    axes[0].axvline(df["total_transacciones"].mean(), color="red",
                    linestyle="--", label=f"Media = {df['total_transacciones'].mean():.1f}")
    axes[0].axvline(df["total_transacciones"].median(), color="green",
                    linestyle="--", label=f"Mediana = {df['total_transacciones'].median():.0f}")
    axes[0].set_title("Distribucion de transacciones por barrio-mes")
    axes[0].set_xlabel("Transacciones")
    axes[0].set_ylabel("Frecuencia")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Q-Q plot contra log
    valores_pos = df[df["total_transacciones"] > 0]["total_transacciones"]
    axes[1].hist(np.log1p(valores_pos), bins=50,
                 color="#F18F01", edgecolor="white")
    axes[1].set_title("Distribucion de log(transacciones + 1)")
    axes[1].set_xlabel("log(transacciones + 1)")
    axes[1].set_ylabel("Frecuencia")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    guardar_figura("08_distribucion_target.png")

    print(f"  Media: {df['total_transacciones'].mean():.2f}")
    print(f"  Mediana: {df['total_transacciones'].median():.0f}")
    print(f"  Std: {df['total_transacciones'].std():.2f}")
    print(f"  Asimetria (skew): {df['total_transacciones'].skew():.2f}")


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("EDA - BARCELONA (2012-2025)")
    print("=" * 60)

    # Cargar datos
    print(f"\nCargando: {ARCHIVO_VISTA1.name}")
    df = pd.read_csv(ARCHIVO_VISTA1, parse_dates=["fecha"])

    print(f"Cargando: {ARCHIVO_VISTA2.name}")
    df_tipo = pd.read_csv(ARCHIVO_VISTA2, parse_dates=["fecha"])

    print(f"  Vista 1: {len(df):,} filas")
    print(f"  Vista 2: {len(df_tipo):,} filas")

    # Ejecutar bloques
    bloque1_serie_temporal(df)
    bloque2_estacionalidad(df)
    bloque3_ranking_barrios(df)
    bloque4_tipologia(df_tipo)
    bloque5_heatmap_barrio_anio(df)
    bloque6_distribucion(df)

    print("\n" + "=" * 60)
    print("EDA COMPLETADO")
    print("=" * 60)
    print(f"Figuras guardadas en: {FIGURAS_DIR}")


if __name__ == "__main__":
    main()