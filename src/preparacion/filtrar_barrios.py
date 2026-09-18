# filtrar_barrios.py
# Aplica los filtros de calidad al dataset agregado.
#
# Decisiones:
# 1. Excluir barrios con >90% de meses sin actividad (ruido puro)
# 2. Excluir agosto 2013 (datos claramente corruptos en la fuente original)

from pathlib import Path
import sys
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.utilidades.config import DATA_PROCESSED


ARCHIVO_ENTRADA_1 = DATA_PROCESSED / "barcelona_barrio_mes.csv"
ARCHIVO_ENTRADA_2 = DATA_PROCESSED / "barcelona_barrio_mes_tipologia.csv"

ARCHIVO_SALIDA_1 = DATA_PROCESSED / "barcelona_barrio_mes_filtrado.csv"
ARCHIVO_SALIDA_2 = DATA_PROCESSED / "barcelona_barrio_mes_tipologia_filtrado.csv"

UMBRAL_CEROS = 0.90
MESES_A_EXCLUIR = [(2013, 8)]  # Agosto 2013


def identificar_barrios_a_excluir(df: pd.DataFrame) -> list:
    """Identifica barrios con >90% de ceros."""
    stats = df.groupby("Nom_Barri")["total_transacciones"].apply(
        lambda x: (x == 0).mean()
    )
    return stats[stats > UMBRAL_CEROS].index.tolist()


def main():
    print("=" * 60)
    print("FILTRADO DE BARRIOS Y MESES CORRUPTOS")
    print("=" * 60)

    df = pd.read_csv(ARCHIVO_ENTRADA_1, parse_dates=["fecha"])
    df_tipo = pd.read_csv(ARCHIVO_ENTRADA_2, parse_dates=["fecha"])

    print(f"\nDataset original:")
    print(f"  Barrios: {df['Nom_Barri'].nunique()}")
    print(f"  Filas vista 1: {len(df):,}")

    # 1. Filtrar barrios
    excluir = identificar_barrios_a_excluir(df)
    print(f"\nBarrios a excluir (>{UMBRAL_CEROS*100:.0f}% ceros): {len(excluir)}")
    for b in excluir:
        pct = (df[df["Nom_Barri"] == b]["total_transacciones"] == 0).mean() * 100
        print(f"  - {b} ({pct:.1f}% ceros)")

    df_filt = df[~df["Nom_Barri"].isin(excluir)].copy()
    df_tipo_filt = df_tipo[~df_tipo["Nom_Barri"].isin(excluir)].copy()

    # 2. Excluir meses corruptos
    print(f"\nExcluyendo meses corruptos conocidos:")
    for anyo, mes in MESES_A_EXCLUIR:
        n_antes = len(df_filt)
        df_filt = df_filt[~((df_filt["Any"] == anyo) & (df_filt["Mes"] == mes))]
        df_tipo_filt = df_tipo_filt[~((df_tipo_filt["Any"] == anyo) &
                                        (df_tipo_filt["Mes"] == mes))]
        print(f"  - {anyo}-{mes:02d}: {n_antes - len(df_filt)} filas eliminadas")

    print(f"\nDataset filtrado final:")
    print(f"  Barrios: {df_filt['Nom_Barri'].nunique()}")
    print(f"  Filas vista 1: {len(df_filt):,}")
    print(f"  Filas vista 2: {len(df_tipo_filt):,}")
    print(f"  Transacciones totales: {df_filt['total_transacciones'].sum():,}")

    print(f"\nFilas por barrio (deberia ser 167):")
    print(df_filt.groupby("Nom_Barri").size().describe().to_string())

    df_filt.to_csv(ARCHIVO_SALIDA_1, index=False, encoding="utf-8")
    df_tipo_filt.to_csv(ARCHIVO_SALIDA_2, index=False, encoding="utf-8")

    print(f"\nGuardado:")
    print(f"  {ARCHIVO_SALIDA_1}")
    print(f"  {ARCHIVO_SALIDA_2}")


if __name__ == "__main__":
    main()