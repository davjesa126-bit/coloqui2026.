"""Interfaz de consola. Ejecutar: python -m brotia.cli"""
import os

from . import capacitacion
from .agente import Agente
from .certificado import generar_certificado
from .config import CONFIG
from .privacidad import pedir_datos


def _cargar_env() -> None:
    if os.path.exists(".env"):
        for linea in open(".env", encoding="utf-8"):
            if "=" in linea and not linea.startswith("#"):
                k, v = linea.strip().split("=", 1)
                os.environ.setdefault(k, v)


def flujo_capacitacion(entrada=input, salida=print) -> None:
    for clase in capacitacion.CLASES:
        salida(f"\n{clase['titulo']}")
        for t in clase["temas"]:
            salida(f"  - {t}")
        entrada("(Enter para continuar) ")
    salida("\nAutoevaluación")
    while True:
        respuestas = []
        for i, p in enumerate(capacitacion.PREGUNTAS, 1):
            salida(f"\n{i}. {p.texto}")
            for j, o in enumerate(p.opciones, 1):
                salida(f"   {j}) {o}")
            while True:
                r = entrada("Tu respuesta: ").strip()
                if r.isdigit() and 1 <= int(r) <= len(p.opciones):
                    respuestas.append(int(r) - 1)
                    break
                salida("Elegí un número de la lista.")
        puntaje, aprobado = capacitacion.evaluar(respuestas)
        salida(f"\nPuntaje: {puntaje}%")
        if aprobado:
            break
        if entrada(f"Necesitás {CONFIG.nota_minima}% para aprobar. ¿Reintentar? (s/n): ").strip().lower() not in ("s", "si", "sí"):
            return
    datos = pedir_datos(entrada, salida)
    if datos is None:
        return
    ruta = generar_certificado(datos, puntaje=puntaje)
    salida(f"\n¡Felicitaciones! Tu certificado está en: {ruta}")


def main() -> None:
    _cargar_env()
    agente = Agente()
    print("BrotIA: asistente de huerta. Escribí tu consulta, /capacitacion para el curso, /salir para terminar.")
    while True:
        msg = input("\nVos: ").strip()
        if msg == "/salir":
            break
        if msg == "/capacitacion":
            flujo_capacitacion()
        elif msg:
            print("BrotIA:", agente.responder(msg))


if __name__ == "__main__":
    main()
