#!/usr/bin/env python3
"""
Importa pronósticos directamente desde fotos de calendarios.

USO:
  1. pip install anthropic
  2. Pon las fotos en la carpeta  calendarios/
     El nombre del fichero = nombre del participante
     Ejemplos:  Adrian Campos.jpg   Carlos Brihuega.jfif   Jose Cuinas.jpeg
  3. Configura tu API key de Anthropic abajo (o variable de entorno ANTHROPIC_API_KEY)
  4. python importar_imagenes.py

El script lee cada imagen con IA y vuelca los 72 pronósticos en data.js.
"""

import json, re, os, sys, base64
from pathlib import Path

# ── Configura aquí tu API key de Anthropic ────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
# ─────────────────────────────────────────────────────────────────────────

MODEL          = "claude-opus-4-8"
SCRIPT_DIR     = Path(__file__).parent
DATA_JS_PATH   = SCRIPT_DIR / "datos" / "data.js"
CALENDARIOS    = SCRIPT_DIR / "calendarios"
EXTENSIONES    = {".jpg", ".jpeg", ".png", ".jfif", ".webp"}

PARTIDOS = """
Grupo A:  (1) México-Sudáfrica  (2) Corea del Sur-Rep. Checa  (3) Rep. Checa-Sudáfrica  (4) México-Corea del Sur  (5) Rep. Checa-México  (6) Sudáfrica-Corea del Sur
Grupo B:  (7) Canadá-Bosnia  (8) Qatar-Suiza  (9) Suiza-Bosnia  (10) Canadá-Qatar  (11) Suiza-Canadá  (12) Bosnia-Qatar
Grupo C:  (13) Brasil-Marruecos  (14) Haití-Escocia  (15) Brasil-Haití  (16) Escocia-Marruecos  (17) Escocia-Brasil  (18) Marruecos-Haití
Grupo D:  (19) EE.UU.-Turquía  (20) Australia-Paraguay  (21) EE.UU.-Australia  (22) Turquía-Paraguay  (23) Turquía-EE.UU.  (24) Paraguay-Australia
Grupo E:  (25) Alemania-Curazao  (26) C.Marfil-Ecuador  (27) Alemania-C.Marfil  (28) Curazao-Ecuador  (29) Ecuador-Alemania  (30) Curazao-C.Marfil
Grupo F:  (31) P.Bajos-Japón  (32) Suecia-Túnez  (33) Japón-Túnez  (34) P.Bajos-Suecia  (35) Túnez-P.Bajos  (36) Japón-Suecia
Grupo G:  (37) Bélgica-Egipto  (38) Irán-N.Zelanda  (39) Bélgica-Irán  (40) Egipto-N.Zelanda  (41) Egipto-Irán  (42) N.Zelanda-Bélgica
Grupo H:  (43) España-C.Verde  (44) Arabia S.-Uruguay  (45) España-Arabia S.  (46) C.Verde-Uruguay  (47) Uruguay-España  (48) C.Verde-Arabia S.
Grupo I:  (49) Francia-Senegal  (50) Irak-Noruega  (51) Francia-Irak  (52) Noruega-Senegal  (53) Noruega-Francia  (54) Senegal-Irak
Grupo J:  (55) Austria-Jordania  (56) Argentina-Argelia  (57) Jordania-Argelia  (58) Argentina-Austria  (59) Jordania-Argentina  (60) Argelia-Austria
Grupo K:  (61) Portugal-RD Congo  (62) Uzbekistán-Colombia  (63) Portugal-Uzbekistán  (64) RD Congo-Colombia  (65) Colombia-Portugal  (66) RD Congo-Uzbekistán
Grupo L:  (67) Inglaterra-Croacia  (68) Ghana-Panamá  (69) Inglaterra-Ghana  (70) Croacia-Panamá  (71) Panamá-Inglaterra  (72) Croacia-Ghana
"""

PROMPT = f"""Esta imagen es un calendario del Mundial 2026 con pronósticos escritos a mano.

Los 72 partidos de la fase de grupos en orden, con su ID entre paréntesis:
{PARTIDOS}

Extrae el marcador (goles local y goles visitante) escrito para cada partido.
El calendario sigue el mismo orden que la lista anterior.

Devuelve ÚNICAMENTE un JSON válido, sin texto adicional:
{{
  "partidos": [
    {{"id": 1, "gl": 2, "gv": 0}},
    {{"id": 2, "gl": 1, "gv": 1}},
    ...
    {{"id": 72, "gl": 2, "gv": 1}}
  ]
}}

Reglas: solo números enteros >= 0. Deben aparecer los 72 partidos."""


def leer_datos():
    txt = DATA_JS_PATH.read_text(encoding="utf-8")
    m = re.search(r"var DATOS\s*=\s*(\{[\s\S]*?\});\s*$", txt, re.MULTILINE)
    return json.loads(m.group(1))

def escribir_datos(d):
    DATA_JS_PATH.write_text(
        "var DATOS = " + json.dumps(d, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8"
    )

def a_base64(path):
    ext = path.suffix.lower().lstrip(".")
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "jfif": "image/jpeg",
            "png": "image/png", "webp": "image/webp"}.get(ext, "image/jpeg")
    return base64.standard_b64encode(path.read_bytes()).decode(), mime

def leer_imagen_con_ia(img_path):
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    b64, mime = a_base64(img_path)
    resp = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": mime, "data": b64}},
                {"type": "text", "text": PROMPT}
            ]
        }]
    )
    texto = resp.content[0].text.strip()
    m = re.search(r"\{[\s\S]*\}", texto)
    if not m:
        raise ValueError(f"Respuesta inesperada: {texto[:300]}")
    resultado = json.loads(m.group())
    partidos = resultado.get("partidos", [])
    if len(partidos) != 72:
        raise ValueError(f"Se esperaban 72 partidos, se recibieron {len(partidos)}")
    return {str(p["id"]): {"gl": int(p["gl"]), "gv": int(p["gv"])} for p in partidos}


def main():
    if not ANTHROPIC_API_KEY:
        print("ERROR: Pon tu API key de Anthropic en la variable ANTHROPIC_API_KEY del script.")
        sys.exit(1)

    imagenes = sorted(f for f in CALENDARIOS.iterdir() if f.suffix.lower() in EXTENSIONES)
    if not imagenes:
        print(f"No hay imágenes en {CALENDARIOS}")
        print("Pon las fotos ahí con el nombre de cada participante y vuelve a ejecutar.")
        return

    datos = leer_datos()

    for img in imagenes:
        nombre = img.stem
        print(f"Leyendo {nombre}...", end=" ", flush=True)
        try:
            apuestas = leer_imagen_con_ia(img)
            if nombre not in datos["pronosticos"]["participantes"]:
                datos["pronosticos"]["participantes"].append(nombre)
            datos["pronosticos"]["apuestas"][nombre] = apuestas
            print("OK")
        except Exception as e:
            print(f"ERROR -> {e}")

    escribir_datos(datos)
    print(f"\nListo. Datos guardados en {DATA_JS_PATH}")


if __name__ == "__main__":
    main()
