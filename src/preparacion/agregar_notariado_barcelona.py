# agregar_notariado_barcelona.py
# Agregacion del dataset del Notariado de Barcelona.
#
# Entrada:
#   data/interim/notariado_barcelona.csv (36.771 filas)
#
# Salidas:
#   data/processed/barcelona_barrio_mes.csv
#   data/processed/barcelona_barrio_mes_tipologia.csv

from pathlib import Path
import sys
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.utilidades.config import DATA_INTERIM, DATA_PROCESSED


ARCHIVO_ENTRADA = DATA_INTERIM / "notariado_barcelona.csv"
ARCHIVO_SALIDA_1 = DATA_PROCESSED / "barcelona_barrio_mes.csv"
ARCHIVO_SALIDA_2 = DATA_PROCESSED / "barcelona_barrio_mes_tipologia.csv"

ANIO_MAX = 2025


def cargar_datos() -> pd.DataFrame:
    """Carga el dataset intermedio."""
    print(f"Cargando: {ARCHIVO_ENTRADA}")
    df = pd.read_csv(ARCHIVO_ENTRADA, encoding="utf-8")
    print(f"  Filas: {len(df):,}")
    return df


def filtrar_y_limpiar(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra años incompletos y limpia valores no utiles."""
    print("\nFiltrando y limpiando...")

    # Excluir 2026 (año incompleto)
    n_antes = len(df)
    df = df[df["Any"] <= ANIO_MAX].copy()
    print(f"  Excluido 2026: {n_antes - len(df):,} filas eliminadas")

    # Excluir 'No consta' (ruido, no aporta info sobre el uso real)
    n_antes = len(df)
    df = df[df["Tipologia_Us_Desc"] != "No consta"].copy()
    print(f"  Excluido 'No consta': {n_antes - len(df):,} filas eliminadas")

    print(f"  Filas finales: {len(df):,}")
    return df


def construir_vista_total(df: pd.DataFrame) -> pd.DataFrame:
    """
    Vista 1: Barrio x Año x Mes, total de transacciones
    (sumando todas las tipologias).
    """
    print("\nConstruyendo vista 1: barrio x año x mes (total)...")

    vista = (
        df.groupby(
            ["Any", "Mes", "Codi_Districte", "Nom_Districte",
             "Codi_Barri", "Nom_Barri"],
            as_index=False,
        )["num_transacciones"]
        .sum()
        .rename(columns={"num_transacciones": "total_transacciones"})
    )

    # Crear columna de fecha
    vista["fecha"] = pd.to_datetime(
        dict(year=vista["Any"], month=vista["Mes"], day=1)
    )

    # Ordenar
    vista = vista.sort_values(
        ["Nom_Barri", "Any", "Mes"]
    ).reset_index(drop=True)

    print(f"  Filas: {len(vista):,}")
    return vista


def construir_vista_tipologia(df: pd.DataFrame) -> pd.DataFrame:
    """
    Vista 2: Barrio x Año x Mes x Tipologia.
    """
    print("\nConstruyendo vista 2: barrio x año x mes x tipología...")

    vista = (
        df.groupby(
            ["Any", "Mes", "Codi_Districte", "Nom_Districte",
             "Codi_Barri", "Nom_Barri", "Tipologia_Us_Codi",
             "Tipologia_Us_Desc"],
            as_index=False,
        )["num_transacciones"]
        .sum()
    )

    vista["fecha"] = pd.to_datetime(
        dict(year=vista["Any"], month=vista["Mes"], day=1)
    )

    vista = vista.sort_values(
        ["Nom_Barri", "Any", "Mes", "Tipologia_Us_Codi"]
    ).reset_index(drop=True)

    print(f"  Filas: {len(vista):,}")
    return vista


def rellenar_meses_faltantes(df: pd.DataFrame, col_grupo: list,
                              col_valor: str = "total_transacciones"
                              ) -> pd.DataFrame:
    """
    Asegura que todos los barrios tengan TODOS los meses del rango
    (rellenando con 0 donde no haya datos).
    """
    print("\nRellenando meses faltantes...")

    # Rango completo de fechas
    fecha_min = df["fecha"].min()
    fecha_max = df["fecha"].max()
    rango_fechas = pd.date_range(fecha_min, fecha_max, freq="MS")

    # Todas las combinaciones posibles de grupo x fecha
    grupos_unicos = df[col_grupo].drop_duplicates()
    grupos_unicos["_key"] = 1
    df_fechas = pd.DataFrame({"fecha": rango_fechas, "_key": 1})
    combinaciones = grupos_unicos.merge(df_fechas, on="_key").drop(columns="_key")

    # Merge con datos originales
    df_completo = combinaciones.merge(
        df, on=col_grupo + ["fecha"], how="left"
    )
    df_completo[col_valor] = df_completo[col_valor].fillna(0).astype(int)

    # Reconstruir Any y Mes
    df_completo["Any"] = df_completo["fecha"].dt.year
    df_completo["Mes"] = df_completo["fecha"].dt.month

    print(f"  Filas antes: {len(df):,}")
    print(f"  Filas después: {len(df_completo):,}")
    return df_completo


def main():
    print("=" * 60)
    print("AGREGACION DEL NOTARIADO - BARCELONA")
    print("=" * 60)

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

    # 1. Cargar
    df = cargar_datos()

    # 2. Filtrar y limpiar
    df = filtrar_y_limpiar(df)

    # 3. Vista total
    vista_total = construir_vista_total(df)

    # 4. Rellenar meses faltantes en vista total
    cols_grupo = ["Codi_Districte", "Nom_Districte",
                  "Codi_Barri", "Nom_Barri"]
    vista_total = rellenar_meses_faltantes(
        vista_total, cols_grupo, "total_transacciones"
    )
    vista_total = vista_total.sort_values(
        ["Nom_Barri", "fecha"]
    ).reset_index(drop=True)

    # 5. Guardar vista total
    vista_total.to_csv(ARCHIVO_SALIDA_1, index=False, encoding="utf-8")
    print(f"\nGuardado: {ARCHIVO_SALIDA_1}")

    # 6. Vista por tipologia (sin rellenar, porque cada barrio-mes
    #    tiene varias tipologias y no todas aplican)
    vista_tipo = construir_vista_tipologia(df)
    vista_tipo.to_csv(ARCHIVO_SALIDA_2, index=False, encoding="utf-8")
    print(f"Guardado: {ARCHIVO_SALIDA_2}")

    # 7. Resumen
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"\nVista 1 (barrio x mes, total):")
    print(f"  Filas: {len(vista_total):,}")
    print(f"  Barrios: {vista_total['Nom_Barri'].nunique()}")
    print(f"  Rango: {vista_total['fecha'].min().date()} → "
          f"{vista_total['fecha'].max().date()}")
    print(f"  Total transacciones: "
          f"{vista_total['total_transacciones'].sum():,}")
    print(f"  Media mensual por barrio: "
          f"{vista_total['total_transacciones'].mean():.1f}")

    print(f"\nVista 2 (barrio x mes x tipologia):")
    print(f"  Filas: {len(vista_tipo):,}")
    print(f"  Tipologias: {vista_tipo['Tipologia_Us_Desc'].nunique()}")
    print(f"  Total transacciones: {vista_tipo['num_transacciones'].sum():,}")

    print(f"\nTransacciones por año (vista 1):")
    print(vista_total.groupby("Any")["total_transacciones"].sum().to_string())

    print(f"\nTop 10 barrios (vista 1):")
    print(
        vista_total.groupby("Nom_Barri")["total_transacciones"]
        .sum().sort_values(ascending=False).head(10).to_string()
    )


if __name__ == "__main__":
    main()