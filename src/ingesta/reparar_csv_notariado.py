# reparar_csv_notariado.py
# Reparador de CSV del Notariado.
#
# Los archivos descargados del portal datos.gob.es vienen con un formato
# roto: cada linea esta entre comillas dobles y las comillas internas
# estan duplicadas.
#
# Ejemplo de linea rota:
#     "2012,1,1,""Ciutat Vella"",1,""el Raval"",9,""No consta"","".."""
#
# Linea reparada:
#     2012,1,1,"Ciutat Vella",1,"el Raval",9,"No consta",..

from pathlib import Path
import sys
import csv

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.utilidades.config import DATA_RAW


CARPETA = DATA_RAW / "notariado"
CARPETA_REPARADA = DATA_RAW / "notariado_limpio"


def reparar_linea(linea: str) -> str:
    """
    Repara una linea del CSV roto.

    Pasos:
    1. Quitar \\r\\n al final
    2. Quitar comillas exteriores si la linea entera esta entre comillas
    3. Reemplazar comillas duplicadas "" por " (dos veces por seguridad)
    """
    linea = linea.rstrip("\r\n")

    # Quitar comillas exteriores si toda la linea esta entre comillas
    if linea.startswith('"') and linea.endswith('"') and linea.count('"') > 2:
        linea = linea[1:-1]

    # Reemplazar comillas duplicadas por simples (dos pasadas)
    linea = linea.replace('""', '"')
    linea = linea.replace('""', '"')

    return linea


def reparar_archivo(ruta_origen: Path, ruta_destino: Path) -> int:
    """Repara un archivo y devuelve el numero de lineas."""
    with open(ruta_origen, "r", encoding="utf-8") as f_in:
        lineas = f_in.readlines()

    lineas_reparadas = [reparar_linea(l) for l in lineas if l.strip()]

    with open(ruta_destino, "w", encoding="utf-8", newline="") as f_out:
        f_out.write("\n".join(lineas_reparadas))

    return len(lineas_reparadas)


def main():
    print("=" * 60)
    print("REPARACION DE CSV DEL NOTARIADO")
    print("=" * 60)

    if not CARPETA.exists():
        print(f"No existe: {CARPETA}")
        return

    CARPETA_REPARADA.mkdir(parents=True, exist_ok=True)

    archivos = sorted(CARPETA.glob("*.csv"))
    print(f"\nArchivos a reparar: {len(archivos)}\n")

    for ruta in archivos:
        ruta_destino = CARPETA_REPARADA / ruta.name
        try:
            n_lineas = reparar_archivo(ruta, ruta_destino)
            print(f"  OK  {ruta.name} -> {n_lineas} lineas")
        except Exception as e:
            print(f"  ERR {ruta.name}: {e}")

    print(f"\nArchivos reparados en: {CARPETA_REPARADA}")

    ejemplo = CARPETA_REPARADA / archivos[0].name
    print(f"\nVerificacion de {ejemplo.name}:")
    with open(ejemplo, "r", encoding="utf-8") as f:
        for i, linea in enumerate(f):
            if i >= 3:
                break
            print(f"   {linea.rstrip()}")


if __name__ == "__main__":
    main()