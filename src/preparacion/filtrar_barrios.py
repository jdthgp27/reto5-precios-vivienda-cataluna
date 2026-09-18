# filtrar_barrios.py
# Aplica el filtro de barrios al dataset agregado.
#
# Decision: excluir barrios con >90% de meses sin actividad.
# Justificacion: aportan menos del 1% de las transacciones totales
# pero anaden ruido al modelo (predicen ceros casi siempre).

from pathlib import Path
import sys
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.utilidades.config import DATA_PROCESSED


ARCHIVO_ENTRADA_1 = DATA_PROCESSED / "barcelona_barrio_mes.csv"
ARCHIVO_ENTRADA_2 = DATA_PROCESSED / "barcelona_barrio_mes_tipologia.csv"

ARCHIVO_SALIDA_1 = DATA_PROCESSED / "barcelona_barrio_mes_filtrado.csv"
ARCHIVO_SALIDA_2 = DATA_PROCESSED / "barcelona_barrio_mes_tipologia_filtrado.csv"

UMBRAL_CEROS = 0.90  # 90%


def identificar_barrios_a_excluir(df: pd.DataFrame) -> list:
    """Identifica barrios con >90% de ceros."""
    stats = df.groupby("Nom_Barri")["total_transacciones"].apply(
        lambda x: (x == 0).mean()
    )
    excluir = stats[stats > UMBRAL_CEROS].index.tolist()
    return excluir


def main():
    print("=" * 60)
    print("FILTRADO DE BARRIOS")
    print("=" * 60)

    # Cargar
    df = pd.read_csv(ARCHIVO_ENTRADA_1, parse_dates=["fecha"])
    df_tipo = pd.read_csv(ARCHIVO_ENTRADA_2, parse_dates=["fecha"])

    print(f"\nDataset original:")
    print(f"  Barrios: {df['Nom_Barri'].nunique()}")
    print(f"  Filas vista 1: {len(df):,}")

    # Identificar barrios a excluir
    excluir = identificar_barrios_a_excluir(df)
    print(f"\nBarrios a excluir (>{UMBRAL_CEROS*100:.0f}% ceros): {len(excluir)}")
    for b in excluir:
        pct = (df[df["Nom_Barri"] == b]["total_transacciones"] == 0).mean() * 100
        print(f"  - {b} ({pct:.1f}% ceros)")

    # Filtrar
    df_filt = df[~df["Nom_Barri"].isin(excluir)].copy()
    df_tipo_filt = df_tipo[~df_tipo["Nom_Barri"].isin(excluir)].copy()

    print(f"\nDataset filtrado:")
    print(f"  Barrios: {df_filt['Nom_Barri'].nunique()}")
    print(f"  Filas vista 1: {len(df_filt):,}")
    print(f"  Filas vista 2: {len(df_tipo_filt):,}")
    print(f"  Transacciones totales: {df_filt['total_transacciones'].sum():,}")

    # Guardar
    df_filt.to_csv(ARCHIVO_SALIDA_1, index=False, encoding="utf-8")
    df_tipo_filt.to_csv(ARCHIVO_SALIDA_2, index=False, encoding="utf-8")

    print(f"\nGuardado:")
    print(f"  {ARCHIVO_SALIDA_1}")
    print(f"  {ARCHIVO_SALIDA_2}")


if __name__ == "__main__":
    main()