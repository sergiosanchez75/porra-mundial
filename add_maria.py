import json, re
from pathlib import Path

DATA_JS = Path(__file__).parent / "datos" / "data.js"
txt = DATA_JS.read_text(encoding="utf-8")
m = re.search(r"var DATOS\s*=\s*(\{[\s\S]*?\});\s*$", txt, re.MULTILINE)
d = json.loads(m.group(1))

nombre = "Maria Lafuente"

# Pronósticos leídos del calendario (gl = goles local, gv = goles visitante)
apuestas = {
    # Grupo A
    "1":  {"gl": 2, "gv": 0},  # México-Sudáfrica
    "2":  {"gl": 1, "gv": 0},  # Corea del Sur-Rep.Checa
    "3":  {"gl": 0, "gv": 1},  # Rep.Checa-Sudáfrica
    "4":  {"gl": 2, "gv": 1},  # México-Corea del Sur
    "5":  {"gl": 1, "gv": 1},  # Rep.Checa-México
    "6":  {"gl": 0, "gv": 1},  # Sudáfrica-Corea del Sur
    # Grupo B
    "7":  {"gl": 1, "gv": 1},  # Canadá-Bosnia
    "8":  {"gl": 0, "gv": 2},  # Qatar-Suiza
    "9":  {"gl": 2, "gv": 0},  # Suiza-Bosnia
    "10": {"gl": 2, "gv": 0},  # Canadá-Qatar
    "11": {"gl": 2, "gv": 1},  # Suiza-Canadá
    "12": {"gl": 1, "gv": 1},  # Bosnia-Qatar
    # Grupo C
    "13": {"gl": 2, "gv": 0},  # Brasil-Marruecos
    "14": {"gl": 0, "gv": 2},  # Haití-Escocia
    "15": {"gl": 3, "gv": 0},  # Brasil-Haití
    "16": {"gl": 1, "gv": 1},  # Escocia-Marruecos
    "17": {"gl": 0, "gv": 2},  # Escocia-Brasil
    "18": {"gl": 2, "gv": 0},  # Marruecos-Haití
    # Grupo D
    "19": {"gl": 2, "gv": 1},  # EE.UU.-Turquía
    "20": {"gl": 1, "gv": 1},  # Australia-Paraguay
    "21": {"gl": 2, "gv": 0},  # EE.UU.-Australia
    "22": {"gl": 2, "gv": 0},  # Turquía-Paraguay
    "23": {"gl": 1, "gv": 2},  # Turquía-EE.UU.
    "24": {"gl": 1, "gv": 2},  # Paraguay-Australia
    # Grupo E
    "25": {"gl": 3, "gv": 0},  # Alemania-Curazao
    "26": {"gl": 1, "gv": 1},  # C.Marfil-Ecuador
    "27": {"gl": 2, "gv": 0},  # Alemania-C.Marfil
    "28": {"gl": 0, "gv": 2},  # Curazao-Ecuador
    "29": {"gl": 0, "gv": 2},  # Ecuador-Alemania
    "30": {"gl": 0, "gv": 2},  # Curazao-C.Marfil
    # Grupo F
    "31": {"gl": 2, "gv": 0},  # P.Bajos-Japón
    "32": {"gl": 2, "gv": 0},  # Suecia-Túnez
    "33": {"gl": 2, "gv": 0},  # Japón-Túnez
    "34": {"gl": 2, "gv": 1},  # P.Bajos-Suecia
    "35": {"gl": 0, "gv": 2},  # Túnez-P.Bajos
    "36": {"gl": 1, "gv": 1},  # Japón-Suecia
    # Grupo G
    "37": {"gl": 2, "gv": 0},  # Bélgica-Egipto
    "38": {"gl": 1, "gv": 1},  # Irán-N.Zelanda
    "39": {"gl": 2, "gv": 1},  # Bélgica-Irán
    "40": {"gl": 1, "gv": 0},  # Egipto-N.Zelanda
    "41": {"gl": 1, "gv": 1},  # Egipto-Irán
    "42": {"gl": 0, "gv": 2},  # N.Zelanda-Bélgica
    # Grupo H
    "43": {"gl": 3, "gv": 0},  # España-C.Verde
    "44": {"gl": 0, "gv": 2},  # Arabia S.-Uruguay
    "45": {"gl": 2, "gv": 0},  # España-Arabia S.
    "46": {"gl": 0, "gv": 3},  # C.Verde-Uruguay
    "47": {"gl": 1, "gv": 2},  # Uruguay-España
    "48": {"gl": 0, "gv": 2},  # C.Verde-Arabia S.
    # Grupo I
    "49": {"gl": 2, "gv": 0},  # Francia-Senegal
    "50": {"gl": 0, "gv": 2},  # Irak-Noruega
    "51": {"gl": 3, "gv": 0},  # Francia-Irak
    "52": {"gl": 1, "gv": 0},  # Noruega-Senegal
    "53": {"gl": 1, "gv": 2},  # Noruega-Francia
    "54": {"gl": 1, "gv": 0},  # Senegal-Irak
    # Grupo J
    "55": {"gl": 2, "gv": 0},  # Austria-Jordania
    "56": {"gl": 3, "gv": 0},  # Argentina-Argelia
    "57": {"gl": 1, "gv": 0},  # Jordania-Argelia
    "58": {"gl": 2, "gv": 1},  # Argentina-Austria
    "59": {"gl": 0, "gv": 3},  # Jordania-Argentina
    "60": {"gl": 1, "gv": 2},  # Argelia-Austria
    # Grupo K
    "61": {"gl": 3, "gv": 0},  # Portugal-RD Congo
    "62": {"gl": 0, "gv": 2},  # Uzbekistán-Colombia
    "63": {"gl": 2, "gv": 0},  # Portugal-Uzbekistán
    "64": {"gl": 0, "gv": 2},  # RD Congo-Colombia
    "65": {"gl": 1, "gv": 2},  # Colombia-Portugal
    "66": {"gl": 0, "gv": 2},  # RD Congo-Uzbekistán
    # Grupo L
    "67": {"gl": 2, "gv": 1},  # Inglaterra-Croacia
    "68": {"gl": 1, "gv": 1},  # Ghana-Panamá
    "69": {"gl": 2, "gv": 0},  # Inglaterra-Ghana
    "70": {"gl": 2, "gv": 0},  # Croacia-Panamá
    "71": {"gl": 0, "gv": 3},  # Panamá-Inglaterra
    "72": {"gl": 1, "gv": 0},  # Croacia-Ghana
}

if nombre not in d["pronosticos"]["participantes"]:
    d["pronosticos"]["participantes"].append(nombre)
    print(f"Añadido participante: {nombre}")
else:
    print(f"Actualizando participante existente: {nombre}")

d["pronosticos"]["apuestas"][nombre] = apuestas

DATA_JS.write_text(
    "var DATOS = " + json.dumps(d, ensure_ascii=False, indent=2) + ";\n",
    encoding="utf-8"
)
print(f"OK - {len(apuestas)} pronósticos guardados para {nombre}")
print(f"Participantes totales: {d['pronosticos']['participantes']}")
