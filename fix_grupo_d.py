import json, re
from pathlib import Path

DATA_JS = Path(__file__).parent / "datos" / "data.js"
txt = DATA_JS.read_text(encoding="utf-8")
m = re.search(r"var DATOS\s*=\s*(\{[\s\S]*?\});\s*$", txt, re.MULTILINE)
d = json.loads(m.group(1))

# Corregir fixture Grupo D
fixes = {19: ("EE.UU.", "Paraguay"), 20: ("Australia", "Turquía"),
         23: ("EE.UU.", "Turquía"),  24: ("Australia", "Paraguay")}
for p in d["partidos"]:
    if p["id"] in fixes:
        viejo = f"{p['local']} vs {p['visitante']}"
        p["local"], p["visitante"] = fixes[p["id"]]
        print(f"Partido {p['id']}: {viejo} -> {p['local']} vs {p['visitante']}")

# Renombrar Adrian Campos -> Adrian OCampo
if "Adrian Campos" in d["pronosticos"]["participantes"]:
    d["pronosticos"]["participantes"] = [
        "Adrian OCampo" if x == "Adrian Campos" else x
        for x in d["pronosticos"]["participantes"]
    ]
    d["pronosticos"]["apuestas"]["Adrian OCampo"] = d["pronosticos"]["apuestas"].pop("Adrian Campos")
    print("Renombrado: Adrian Campos -> Adrian OCampo")

DATA_JS.write_text("var DATOS = " + json.dumps(d, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
print("OK - data.js actualizado")
