"""Conversación con IA. SIN PROBAR contra la API real: revisá antes de usar en producción."""
import csv
import os
from pathlib import Path
from typing import List

RAIZ = Path(__file__).resolve().parent.parent

REGLAS = """Sos BrotIA, un asistente de huerta en casa pensado para Formosa y Chaco (Argentina).
Reglas:
- Respondé en español, claro y breve.
- No te presentes como INTA ni como organismo público. Podés citar materiales del INTA como fuente.
- El calendario de siembra de tu base es nacional (ProHuerta) y NO está validado para el NEA:
  avisá que las fechas deben ajustarse al clima local (calor, heladas, lluvias).
- Ciclo lunar y viento: presentalos como saberes tradicionales; las fuentes a veces se contradicen
  y no son reglas garantizadas.
- No inventes datos. Si no sabés o la fila dice 'Verificar', decilo.
- No pidas datos personales. Los datos para el certificado se piden solo en el flujo /capacitacion.
"""


def cargar_calendario() -> str:
    """Devuelve filas del CSV excepto las marcadas 'Verificar'."""
    ruta = RAIZ / "datos" / "calendario_siembra.csv"
    if not ruta.exists():
        return ""
    with open(ruta, encoding="utf-8", newline="") as f:
        filas = [r for r in csv.DictReader(f) if r.get("Confianza") != "Verificar"]
    return "\n".join(
        f"{r['Cultivo']}: {r['Forma de siembra']}; {r['Época']}; plantas {r['Entre plantas (cm)']} cm x líneas "
        f"{r['Entre líneas (cm)']} cm; cosecha {r['Días a cosecha']} días ({r['Confianza']})" for r in filas)


class Agente:
    def __init__(self) -> None:
        self.historial: List[dict] = []
        self.sistema = REGLAS + "\nBase de calendario:\n" + cargar_calendario()

    def responder(self, mensaje: str) -> str:
        try:
            import anthropic
        except ImportError:
            return "Falta instalar el paquete 'anthropic' (pip install anthropic)."
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return "Falta ANTHROPIC_API_KEY en el entorno (ver .env.example)."
        self.historial.append({"role": "user", "content": mensaje})
        cliente = anthropic.Anthropic()
        resp = cliente.messages.create(
            model=os.environ.get("BROTIA_MODEL", "claude-sonnet-5-5"),
            max_tokens=1000, system=self.sistema, messages=self.historial)
        texto = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        self.historial.append({"role": "assistant", "content": texto})
        return texto
