"""Capacitación de cuatro clases y autoevaluación."""
from dataclasses import dataclass
from typing import List, Tuple

from .config import CONFIG

CLASES = [
    {"titulo": "Clase 1: Qué sembrar y cómo empezar la huerta",
     "temas": ["Qué sembrar en cada época del año",
               "Cómo hacer una huerta desde cero",
               "Huerta a menor y mayor escala"]},
    {"titulo": "Clase 2: Siembra, distancias y riego",
     "temas": ["Métodos de siembra (directa, almácigo y trasplante)",
               "Distancia entre plantas y entre líneas",
               "Croquis de huerta y sistemas de riego"]},
    {"titulo": "Clase 3: Cuidados, cosechas y semillas",
     "temas": ["Cuidados y manejo",
               "Métodos de cosecha",
               "Conservación de semillas"]},
    {"titulo": "Clase 4: Agroecología y saberes tradicionales",
     "temas": ["Rotación y asociación de cultivos",
               "Conocimientos campesinos: ciclo lunar y ciclo del viento",
               "Presentados como saberes tradicionales, no como reglas garantizadas"]},
]


@dataclass
class Pregunta:
    texto: str
    opciones: List[str]
    correcta: int  # índice base 0


PREGUNTAS = [
    Pregunta("¿Cómo se siembra la zanahoria según el INTA?",
             ["Siempre en siembra directa, nunca trasplantada", "Solo en almácigo", "Indistintamente"], 0),
    Pregunta("¿Cuántos días tarda aproximadamente el rabanito hasta la cosecha?",
             ["25 a 30 días", "90 a 100 días", "150 días"], 0),
    Pregunta("La 'chacra' de ProHuerta es una asociación de:",
             ["Tomate, lechuga y zanahoria", "Maíz, zapallo y poroto", "Papa, cebolla y ajo"], 1),
    Pregunta("¿Cómo se secan las semillas cosechadas?",
             ["Al sol directo en una chapa", "A la sombra, con buena ventilación y al menos 10 días", "En la heladera, mojadas"], 1),
    Pregunta("Regla general de distancias: a mayor tamaño de la planta y ciclo más largo...",
             ["Mayor distancia entre plantas", "Menor distancia entre plantas", "No cambia la distancia"], 0),
    Pregunta("La asociación de cultivos sirve para:",
             ["Aprovechar mejor el espacio y ayudar al control de plagas", "Evitar el riego", "Eliminar la rotación"], 0),
    Pregunta("Para producir semillas, ¿cuándo se suspende el riego?",
             ["Al sembrar", "Desde la madurez o cuando las flores empiezan a secarse", "Nunca se suspende"], 1),
    Pregunta("Según saberes tradicionales y un trabajo de la UNNE, la lechuga se siembra en cuarto menguante para:",
             ["Obtener hojas grandes y que no espigue rápido", "Que dé más frutos", "Que germine sin agua"], 0),
]


def evaluar(respuestas: List[int]) -> Tuple[int, bool]:
    """respuestas: índices base 0, en el orden de PREGUNTAS. Devuelve (porcentaje, aprobado)."""
    if len(respuestas) != len(PREGUNTAS):
        raise ValueError("Cantidad de respuestas incorrecta.")
    aciertos = sum(1 for r, p in zip(respuestas, PREGUNTAS) if r == p.correcta)
    porcentaje = round(100 * aciertos / len(PREGUNTAS))
    return porcentaje, porcentaje >= CONFIG.nota_minima
