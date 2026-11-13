"""Configuración central. Editá acá los datos de la entidad y los firmantes."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


RAIZ = Path(__file__).resolve().parent.parent
FIRMAS = RAIZ / "firmas"
LOGO = RAIZ / "assets" / "logo.png"


@dataclass
class Firmante:
    nombre: str
    titulo: str
    # Ruta a una imagen de firma (PNG). Usar SOLO con autorización de la persona.
    imagen: Optional[str] = None


@dataclass
class Config:
    entidad: str = "BrotIA"
    curso: str = "Capacitación en Huerta Agroecológica"
    lema: str = "Conectando naturaleza y tecnología"
    logo: str = str(LOGO)
    nota_minima: int = 70  # porcentaje para aprobar la autoevaluación
    # Orden de firmas tal como lo indicó la organización. Las imágenes viven en firmas/ (fuera de git).
    firmantes: List[Firmante] = field(default_factory=lambda: [
        Firmante("Amadey Alex", "Profesor en Agronomía", str(FIRMAS / "amadey_alex.png")),
        Firmante("Aguilera David", "Técnico en Agroindustria", str(FIRMAS / "aguilera_david.png")),
        Firmante("Zabala Matías", "Técnico en Alimentos", str(FIRMAS / "zabala_matias.png")),
    ])
    aclaracion: str = "Certificado de participación emitido por BrotIA."


CONFIG = Config()
