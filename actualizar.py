#!/usr/bin/env python3
"""
Porra Mundial 2026 — Actualizador diario de resultados
=======================================================
Obtiene los resultados de football-data.org y actualiza datos/data.js.

CONFIGURACIÓN INICIAL (hacer solo una vez):
  1. Regístrate gratis en https://www.football-data.org/client/register
  2. Copia tu API key y ponla abajo en API_KEY, o defínela como variable
     de entorno:  set FOOTBALL_API_KEY=tu_clave_aqui
  3. Programa este script con el Programador de Tareas de Windows:
       Acción: python.exe  "ruta\\actualizar.py"
       Desencadenador: diario, a las 08:00

El log se escribe en actualizar.log junto a este fichero.
"""

import json
import re
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# ── Configuración ──────────────────────────────────────────────────────────
API_KEY  = os.getenv("FOOTBALL_API_KEY", "5e699c682ef348eebbab8f32c91e44f4")
API_URL  = "https://api.football-data.org/v4/competitions/WC/matches"

SCRIPT_DIR   = Path(__file__).parent
DATA_JS_PATH = SCRIPT_DIR / "datos" / "data.js"
LOG_PATH     = SCRIPT_DIR / "actualizar.log"

# Mapeo: nombre en la API → nombre en data.js
NOMBRES = {
    "Mexico": "México",
    "South Africa": "Sudáfrica",
    "Korea Republic": "Corea del Sur",
    "South Korea": "Corea del Sur",
    "Czech Republic": "Rep. Checa",
    "Czechia": "Rep. Checa",
    "Canada": "Canadá",
    "Bosnia and Herzegovina": "Bosnia",
    "Bosnia-Herzegovina": "Bosnia",
    "Switzerland": "Suiza",
    "Brazil": "Brasil",
    "Morocco": "Marruecos",
    "Haiti": "Haití",
    "Scotland": "Escocia",
    "United States": "EE.UU.",
    "USA": "EE.UU.",
    "Turkey": "Turquía",
    "Türkiye": "Turquía",
    "Germany": "Alemania",
    "Curaçao": "Curazao",
    "Cote D'Ivoire": "C. Marfil",
    "Côte d'Ivoire": "C. Marfil",
    "Ivory Coast": "C. Marfil",
    "Netherlands": "P. Bajos",
    "Japan": "Japón",
    "Sweden": "Suecia",
    "Tunisia": "Túnez",
    "Belgium": "Bélgica",
    "Egypt": "Egipto",
    "Iran": "Irán",
    "New Zealand": "N. Zelanda",
    "Spain": "España",
    "Cape Verde": "C. Verde",
    "Cabo Verde": "C. Verde",
    "Cape Verde Islands": "C. Verde",
    "Saudi Arabia": "Arabia S.",
    "France": "Francia",
    "Senegal": "Senegal",
    "Iraq": "Irak",
    "Norway": "Noruega",
    "Austria": "Austria",
    "Jordan": "Jordania",
    "Argentina": "Argentina",
    "Algeria": "Argelia",
    "Portugal": "Portugal",
    "DR Congo": "RD Congo",
    "Congo DR": "RD Congo",
    "Uzbekistan": "Uzbekistán",
    "Colombia": "Colombia",
    "England": "Inglaterra",
    "Croatia": "Croacia",
    "Ghana": "Ghana",
    "Panama": "Panamá",
    "Panamá": "Panamá",
    "Australia": "Australia",
    "Paraguay": "Paraguay",
    "Ecuador": "Ecuador",
    "Uruguay": "Uruguay",
    "Qatar": "Qatar",
}
# ──────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def normalizar(nombre):
    return NOMBRES.get(nombre, nombre)


def fetch_resultados():
    """Descarga partidos finalizados de la API. Devuelve {(local, visitante): (gl, gv)}."""
    import urllib.request
    import ssl

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(API_URL, headers={"X-Auth-Token": API_KEY})
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            data = json.loads(resp.read())
    except Exception as exc:
        log.error("Error al conectar con la API: %s", exc)
        return None

    resultados = {}
    for m in data.get("matches", []):
        if m.get("status") != "FINISHED":
            continue
        local     = normalizar(m["homeTeam"]["name"])
        visitante = normalizar(m["awayTeam"]["name"])
        ft        = m.get("score", {}).get("fullTime", {})
        gl, gv    = ft.get("home"), ft.get("away")
        if gl is not None and gv is not None:
            resultados[(local, visitante)] = (int(gl), int(gv))
            log.info("  Resultado: %s %d-%d %s", local, gl, gv, visitante)

    log.info("Partidos finalizados en la API: %d", len(resultados))
    return resultados


def leer_datos():
    content = DATA_JS_PATH.read_text(encoding="utf-8")
    m = re.search(r"var DATOS\s*=\s*(\{[\s\S]*?\});\s*$", content, re.MULTILINE)
    if not m:
        raise ValueError("No se encontró 'var DATOS = ...' en data.js")
    return json.loads(m.group(1))


def escribir_datos(datos):
    datos["ultimaActualizacion"] = datetime.now().isoformat(timespec="seconds")
    js = "var DATOS = " + json.dumps(datos, ensure_ascii=False, indent=2) + ";\n"
    DATA_JS_PATH.write_text(js, encoding="utf-8")


def main():
    log.info("=== Inicio actualización ===")

    if not API_KEY:
        msg = "Falta la API key. Edita actualizar.py o define FOOTBALL_API_KEY."
        log.error(msg)
        print("ERROR:", msg)
        sys.exit(1)

    resultados_api = fetch_resultados()
    if resultados_api is None:
        print("ERROR: no se pudo conectar con la API. Revisa actualizar.log.")
        sys.exit(1)

    if not resultados_api:
        log.info("No hay resultados nuevos.")
        print("OK: No hay partidos finalizados aún.")
        return

    datos = leer_datos()

    # Índice (local, visitante) → id de partido
    lookup = {(p["local"], p["visitante"]): p["id"] for p in datos["partidos"]}

    actualizados = 0
    sin_mapeo = []
    for (local, visitante), (gl, gv) in resultados_api.items():
        pid = lookup.get((local, visitante))
        if pid is None:
            sin_mapeo.append(f"{local} vs {visitante}")
            continue
        datos["resultados"][str(pid)] = {"gl": gl, "gv": gv}
        actualizados += 1

    if sin_mapeo:
        log.warning("Partidos sin mapeo: %s", ", ".join(sin_mapeo))

    escribir_datos(datos)
    log.info("=== Fin: %d resultados guardados ===", actualizados)
    print(f"OK: {actualizados} resultados actualizados. Log: {LOG_PATH}")


if __name__ == "__main__":
    main()
