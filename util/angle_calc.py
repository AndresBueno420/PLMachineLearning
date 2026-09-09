import math
import requests

BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
COMPETITION_ID = 2
SEASON_ID = 27  # 2015/2016

# StatsBomb usa una cancha de 120 (largo) x 80 (ancho) unidades.
# El arco rival SIEMPRE esta en x=120, centrado en y=40 (sin importar
# si el equipo jugo de local o visitante - StatsBomb ya normaliza eso).
# El ancho real de un arco es 7.32m; en esta escala equivale
# aproximadamente a 8 unidades, asi que los postes quedan en y=36 y y=44.
ARCO_X = 120
POSTE_1 = (ARCO_X, 36)
POSTE_2 = (ARCO_X, 44)
CENTRO_ARCO = (ARCO_X, 40)


def obtener_partidos(competition_id: int, season_id: int) -> list:
    url = f"{BASE_URL}/matches/{competition_id}/{season_id}.json"
    respuesta = requests.get(url)
    respuesta.raise_for_status()
    return respuesta.json()


def obtener_eventos(match_id: int) -> list:
    url = f"{BASE_URL}/events/{match_id}.json"
    respuesta = requests.get(url)
    respuesta.raise_for_status()
    return respuesta.json()


def filtrar_tiros(eventos: list) -> list:
    return [e for e in eventos if e["type"]["name"] == "Shot"]


def calcular_distancia(x: float, y: float) -> float:
    """Distancia en linea recta desde el punto de tiro al centro del arco."""
    return math.hypot(CENTRO_ARCO[0] - x, CENTRO_ARCO[1] - y)


def calcular_angulo(x: float, y: float) -> float:
    """
    Angulo (en grados) que abarca el arco visto desde el punto de tiro.

    NO es el angulo hacia el centro del arco - es el angulo ENTRE los
    dos postes. Lo calculamos sacando el angulo (con atan2) desde el
    punto de tiro hacia cada poste, y restando esos dos angulos.
    """
    angulo_poste_1 = math.atan2(POSTE_1[1] - y, POSTE_1[0] - x)
    angulo_poste_2 = math.atan2(POSTE_2[1] - y, POSTE_2[0] - x)
    angulo = abs(angulo_poste_1 - angulo_poste_2)

    # Si el resultado da mas de 180 grados, estamos midiendo el "lado
    # largo" del angulo entre los dos vectores - lo corregimos al lado
    # corto, que es el que realmente importa.
    if angulo > math.pi:
        angulo = 2 * math.pi - angulo

    return math.degrees(angulo)


if __name__ == "__main__":
    partidos = obtener_partidos(COMPETITION_ID, SEASON_ID)
    partido = partidos[0]
    match_id = partido["match_id"]

    eventos = obtener_eventos(match_id)
    tiros = filtrar_tiros(eventos)

    print(f"{'Jugador':<25} {'Distancia':>10} {'Angulo':>8}   Resultado")
    print("-" * 60)
    for tiro in tiros:
        x, y = tiro["location"]
        distancia = calcular_distancia(x, y)
        angulo = calcular_angulo(x, y)
        jugador = tiro["player"]["name"]
        resultado = tiro["shot"]["outcome"]["name"]
        print(f"{jugador:<25} {distancia:10.1f} {angulo:8.1f}   {resultado}")