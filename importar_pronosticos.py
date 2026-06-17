#!/usr/bin/env python3
"""
Porra Mundial 2026 — Importador de pronósticos
===============================================
Lee un fichero de pronósticos (CSV o texto) y lo añade a datos/data.js.

Uso:
  python importar_pronosticos.py "Jose Cuinas" pronosticos_jose.csv

Formato CSV esperado (una fila por partido):
  id_partido,goles_local,goles_visitante
  Ejemplo:
    1,2,1
    2,0,0
    3,1,2
    ...

También acepta formato "local-visitante":
    México,2,1
    Corea del Sur,0,0
    ...
"""

import json
import re
import sys
import csv
from pathlib import Path

SCRIPT_DIR   = Path(__file__).parent
DATA_JS_PATH = SCRIPT_DIR / "datos" / "data.js"


def leer_datos():
    content = DATA_JS_PATH.read_text(encoding="utf-8")
    m = re.search(r"var DATOS\s*=\s*(\{[\s\S]*?\});\s*$", content, re.MULTILINE)
    if not m:
        raise ValueError("No se encontró 'var DATOS = ...' en data.js")
    return json.loads(m.group(1))


def escribir_datos(datos):
    js = "var DATOS = " + json.dumps(datos, ensure_ascii=False, indent=2) + ";\n"
    DATA_JS_PATH.write_text(js, encoding="utf-8")


def importar(nombre, fichero):
    datos = leer_datos()
    partidos = {p["id"]: p for p in datos["partidos"]}
    # Also index by local team name for flexible import
    por_local = {p["local"]: p["id"] for p in datos["partidos"]}

    if nombre not in datos["pronosticos"]["participantes"]:
        datos["pronosticos"]["participantes"].append(nombre)

    apuestas = datos["pronosticos"]["apuestas"].setdefault(nombre, {})

    with open(fichero, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for fila in reader:
            fila = [c.strip() for c in fila if c.strip()]
            if not fila or fila[0].startswith("#"):
                continue

            if len(fila) == 3:
                try:
                    # Format: id, gl, gv
                    pid = int(fila[0])
                    gl  = int(fila[1])
                    gv  = int(fila[2])
                except ValueError:
                    # Format: equipo_local, gl, gv
                    equipo = fila[0]
                    pid    = por_local.get(equipo)
                    if pid is None:
                        print(f"  AVISO: equipo '{equipo}' no encontrado, fila ignorada.")
                        continue
                    gl, gv = int(fila[1]), int(fila[2])

                apuestas[str(pid)] = {"gl": gl, "gv": gv}
                print(f"  Partido {pid}: {gl}-{gv}")
            else:
                print(f"  AVISO: fila ignorada: {fila}")

    escribir_datos(datos)
    print(f"\nOK: {len(apuestas)} pronósticos guardados para '{nombre}'.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    importar(sys.argv[1], sys.argv[2])
