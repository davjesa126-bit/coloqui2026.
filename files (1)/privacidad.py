"""Aviso de privacidad y pedido de datos con consentimiento voluntario.

IMPORTANTE: el texto del aviso es un BORRADOR. Conviene que lo revise una persona
con conocimiento legal (en Argentina rige la Ley 25.326 de Protección de Datos
Personales; el organismo de control es la Agencia de Acceso a la Información Pública).
"""
import re
from dataclasses import dataclass
from typing import Callable, Optional

AVISO = """AVISO SOBRE TUS DATOS PERSONALES
Para emitir tu certificado necesitamos tu NOMBRE COMPLETO y tu DNI.
- Para qué: únicamente para escribirlos en el certificado en PDF y generar su código de verificación.
- Es voluntario: podés negarte. Si no los das, podés seguir usando BrotIA y hacer la
  capacitación, pero no se emite el certificado.
- No los guardamos: se usan en el momento y no se almacenan en ningún servidor de BrotIA.
  El PDF queda solo en tu dispositivo (o donde lo descargues).
- No los compartimos con terceros.
- Tus derechos: si algún día se guardaran, podrás pedir acceso, corrección o eliminación.
"""

PREGUNTA_CONSENTIMIENTO = "¿Aceptás darnos tu nombre completo y DNI para emitir el certificado? (s/n): "


@dataclass
class Datos:
    nombre: str
    dni: str  # solo dígitos

    def __repr__(self) -> str:  # evita filtrar el DNI en logs
        return f"Datos(nombre={self.nombre!r}, dni='***{self.dni[-3:]}')"


def normalizar_dni(texto: str) -> Optional[str]:
    """Acepta '12.345.678' o '12345678'. Devuelve solo dígitos o None si no es válido."""
    digitos = re.sub(r"[.\s-]", "", texto or "")
    return digitos if re.fullmatch(r"\d{7,8}", digitos) else None


def normalizar_nombre(texto: str) -> Optional[str]:
    limpio = re.sub(r"\s+", " ", (texto or "").strip())
    if len(limpio) < 5 or " " not in limpio:
        return None  # pedimos nombre y apellido
    return limpio


def pedir_datos(entrada: Callable[[str], str] = input,
                salida: Callable[[str], None] = print) -> Optional[Datos]:
    """Muestra el aviso y pide los datos solo si la persona acepta. Devuelve None si no."""
    salida(AVISO)
    if entrada(PREGUNTA_CONSENTIMIENTO).strip().lower() not in ("s", "si", "sí"):
        salida("Entendido, no te pedimos ningún dato. No se emitirá certificado.")
        return None
    while True:
        nombre = normalizar_nombre(entrada("Nombre y apellido completos: "))
        if nombre:
            break
        salida("Escribí nombre y apellido.")
    while True:
        dni = normalizar_dni(entrada("DNI (solo números): "))
        if dni:
            break
        salida("El DNI debe tener 7 u 8 números.")
    return Datos(nombre=nombre, dni=dni)
