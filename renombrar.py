#!/usr/bin/env python3
"""
Renombra un participante en data.js
Uso: python renombrar.py "NombreViejo" "NombreNuevo"
"""
import json, re, sys
from pathlib import Path

DATA_JS = Path(__file__).parent / "datos" / "data.js"

def leer():
    m = re.search(r"var DATOS\s*=\s*(\{[\s\S]*?\});\s*$",
                  DATA_JS.read_text(encoding="utf-8"), re.MULTILINE)
    return json.loads(m.group(1))

def escribir(d):
    DATA_JS.write_text("var DATOS = " + json.dumps(d, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")

if len(sys.argv) != 3:
    print("Uso: python renombrar.py \"NombreViejo\" \"NombreNuevo\"")
    sys.exit(1)

viejo, nuevo = sys.argv[1], sys.argv[2]
datos = leer()
participantes = datos["pronosticos"]["participantes"]

if viejo not in participantes:
    print(f"ERROR: '{viejo}' no existe.")
    print("Participantes actuales:", participantes)
    sys.exit(1)

datos["pronosticos"]["participantes"] = [nuevo if p == viejo else p for p in participantes]
datos["pronosticos"]["apuestas"][nuevo] = datos["pronosticos"]["apuestas"].pop(viejo)
escribir(datos)
print(f"OK: '{viejo}' → '{nuevo}'")
