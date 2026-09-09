"""
Fase 1 - Paso 1 (definitivo): Explorar los datos de tiros con StatsBomb Open Data

DECISION DE FUENTE DE DATOS (documentada para el README mas adelante):
Intentamos primero con Understat.com (scraping) porque ofrecia continuidad
historica + temporada actual. Verificamos empiricamente que el sitio ya
no embebe los datos como JSON dentro del HTML (la respuesta no traia
ninguna variable "JSON.parse", y la pagina es demasiado pequena para
contener el calendario completo) - probablemente ahora los cargan via
una llamada interna que no replicamos con un GET simple. En vez de
perseguir esa llamada (fragil, no pensada para consumo publico), volvimos
a StatsBomb Open Data: licencia abierta oficial, datos servidos como
archivos JSON estaticos en GitHub, sin scraping de ningun tipo.

Trade-off aceptado: solo 2 temporadas de Premier League (2003/04 y
2015/16), pero con muchisimo mas detalle por tiro (freeze_frame con
posiciones de defensores, tecnica del disparo, presion, etc.) y datos
100% estables.

Jerarquia de datos (todo son JSON estaticos, sin auth):
  matches/{competition_id}/{season_id}.json   -> lista de partidos
    -> events/{match_id}.json                  -> eventos de ESE partido
"""

import json
import requests

BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"

# Premier League: competition_id = 2
# Temporadas disponibles en el open data: 2015/2016 (season_id=27) y 2003/2004 (season_id=44)
COMPETITION_ID = 2
SEASON_ID = 27  # 2015/2016 - la del titulo del Leicester


def obtener_partidos(competition_id: int, season_id: int) -> list:
    """Trae la lista completa de partidos de una temporada."""
    url = f"{BASE_URL}/matches/{competition_id}/{season_id}.json"
    respuesta = requests.get(url)
    respuesta.raise_for_status()
    return respuesta.json()


def obtener_eventos(match_id: int) -> list:
    """Trae TODOS los eventos (pases, tiros, faltas, todo) de un partido."""
    url = f"{BASE_URL}/events/{match_id}.json"
    respuesta = requests.get(url)
    respuesta.raise_for_status()
    return respuesta.json()


def filtrar_tiros(eventos: list) -> list:
    """De todos los eventos de un partido, nos quedamos solo con los tiros."""
    return [e for e in eventos if e["type"]["name"] == "Shot"]


if __name__ == "__main__":
    partidos = obtener_partidos(COMPETITION_ID, SEASON_ID)
    print(f"Partidos encontrados en la temporada: {len(partidos)}")

    # Tomamos el primer partido de la lista para explorar
    partido = partidos[0]
    nombre_local = partido["home_team"]["home_team_name"]
    nombre_visitante = partido["away_team"]["away_team_name"]
    print(f"Partido elegido: {nombre_local} vs {nombre_visitante}")

    match_id = partido["match_id"]
    eventos = obtener_eventos(match_id)
    tiros = filtrar_tiros(eventos)
    print(f"Tiros en este partido: {len(tiros)}")

    # Miramos un tiro completo, tal cual viene
    print("\nUn tiro de ejemplo:")
    print(json.dumps(tiros[0], indent=2))

    # Un vistazo rapido a los resultados de TODOS los tiros de este partido,
    # para que veas la variedad de outcomes antes de definir el target
    outcomes = [t["shot"]["outcome"]["name"] for t in tiros]
    print(f"\nOutcomes distintos en este partido: {set(outcomes)}")
    print(f"Goles en este partido: {outcomes.count('Goal')}")