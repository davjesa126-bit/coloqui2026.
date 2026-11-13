"""Generación de certificados en PDF (diseño verde con motivos de naturaleza) y código de verificación."""
import hashlib
import hmac
import io
import math
import os
import random
from datetime import date
from typing import Optional, Tuple

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

from .config import CONFIG, Config
from .privacidad import Datos

VERDE_OSCURO = HexColor("#0E3B28")
VERDE = HexColor("#1F6B3F")
VERDE_CLARO = HexColor("#5FBF5A")
VERDE_HOJA = HexColor("#2E8B4A")
AZUL = HexColor("#2F5FD0")
ORO = HexColor("#C9A227")
CREMA = HexColor("#FBF8EE")
GRIS = HexColor("#4A4A4A")


# ---------- código de verificación ----------
def _secreto(secreto: Optional[str]) -> bytes:
    valor = secreto or os.environ.get("BROTIA_SECRET")
    if not valor:
        raise RuntimeError("Falta BROTIA_SECRET (ver .env.example).")
    return valor.encode()


def codigo_verificacion(datos: Datos, fecha_iso: str, curso: str, secreto: Optional[str] = None) -> str:
    """Código XXXX-XXXX-XXXX derivado con HMAC. No contiene datos personales legibles."""
    mensaje = f"{datos.nombre.lower()}|{datos.dni}|{fecha_iso}|{curso}".encode()
    h = hmac.new(_secreto(secreto), mensaje, hashlib.sha256).hexdigest().upper()[:12]
    return "-".join(h[i:i + 4] for i in range(0, 12, 4))


def verificar(datos: Datos, fecha_iso: str, codigo: str, curso: str = CONFIG.curso,
              secreto: Optional[str] = None) -> bool:
    """Comprueba si un código corresponde a esos datos (quien verifica debe tenerlos)."""
    esperado = codigo_verificacion(datos, fecha_iso, curso, secreto)
    return hmac.compare_digest(esperado, (codigo or "").strip().upper())


def _formatear_dni(dni: str) -> str:
    return f"{int(dni):,}".replace(",", ".")


# ---------- elementos decorativos ----------
def _hoja(c, x, y, largo, angulo, color, alpha=1.0, nervadura=True):
    c.saveState()
    c.translate(x, y); c.rotate(angulo)
    c.setFillColor(color); c.setFillAlpha(alpha)
    p = c.beginPath()
    p.moveTo(0, 0)
    p.curveTo(largo * .25, largo * .36, largo * .75, largo * .30, largo, 0)
    p.curveTo(largo * .75, -largo * .30, largo * .25, -largo * .36, 0, 0)
    c.drawPath(p, fill=1, stroke=0)
    if nervadura:
        c.setStrokeColor(Color(1, 1, 1, alpha=min(alpha, .45))); c.setLineWidth(.6)
        c.line(largo * .05, 0, largo * .92, 0)
    c.restoreState()


def _rama(c, x0, y0, angulo, largo, hojas, tam_hoja, color, alpha=1.0, curva=0.25):
    """Rama curva con hojas alternadas. El ángulo está en grados."""
    a = math.radians(angulo)
    n = hojas
    pts = []
    for i in range(n + 1):
        t = i / n
        d = largo * t
        desvio = curva * largo * t * t
        px = x0 + math.cos(a) * d - math.sin(a) * desvio
        py = y0 + math.sin(a) * d + math.cos(a) * desvio
        pts.append((px, py))
    c.saveState()
    c.setStrokeColor(color); c.setFillAlpha(alpha); c.setStrokeAlpha(alpha); c.setLineWidth(2)
    p = c.beginPath(); p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    c.drawPath(p, fill=0, stroke=1)
    c.restoreState()
    for i, (px, py) in enumerate(pts[1:], 1):
        tamanio = tam_hoja * (1.0 - 0.45 * i / n)
        lado = 1 if i % 2 else -1
        ang_local = angulo + lado * 42 + curva * 25 * i / n * 10
        _hoja(c, px, py, tamanio, ang_local, color, alpha)
    _hoja(c, pts[-1][0], pts[-1][1], tam_hoja * .5, angulo + curva * 25, color, alpha)


def _texto_espaciado(c, x_centro, y, texto, fuente, tam, espacio):
    ancho = stringWidth(texto, fuente, tam) + espacio * (len(texto) - 1)
    t = c.beginText(x_centro - ancho / 2, y)
    t.setFont(fuente, tam); t.setCharSpace(espacio); t.textOut(texto); t.setCharSpace(0)
    c.drawText(t)


def _fondo(c, ancho, alto):
    c.linearGradient(0, 0, 0, alto, (VERDE_OSCURO, VERDE), (0, 1), extend=True)
    # hojas translúcidas y destellos, estilo "naturaleza + tecnología"
    rnd = random.Random(7)
    for _ in range(46):
        x = rnd.choice([rnd.uniform(0, 70), rnd.uniform(ancho - 70, ancho)]) if rnd.random() < .7 else rnd.uniform(0, ancho)
        y = rnd.uniform(0, alto)
        _hoja(c, x, y, rnd.uniform(28, 70), rnd.uniform(0, 360), VERDE_CLARO, alpha=rnd.uniform(.08, .2))
    c.setFillColor(HexColor("#7CF0C5"))
    for _ in range(70):
        c.setFillAlpha(rnd.uniform(.25, .7))
        c.circle(rnd.uniform(0, ancho), rnd.uniform(0, alto), rnd.uniform(.6, 1.8), fill=1, stroke=0)
    c.setFillAlpha(1)


def _medallon(c, cx, cy, radio, ruta_logo):
    c.setFillColor(ORO); c.circle(cx, cy, radio + 7, fill=1, stroke=0)
    c.setFillColor(CREMA); c.circle(cx, cy, radio + 3.5, fill=1, stroke=0)
    if ruta_logo and os.path.exists(ruta_logo):
        c.saveState()
        p = c.beginPath(); p.circle(cx, cy, radio); c.clipPath(p, stroke=0, fill=0)
        c.drawImage(ruta_logo, cx - radio, cy - radio, 2 * radio, 2 * radio, mask="auto")
        c.restoreState()
    else:
        c.setFillColor(VERDE); c.circle(cx, cy, radio, fill=1, stroke=0)


# ---------- dibujo principal ----------
def _dibujar(c, datos: Datos, codigo: str, fecha: date, puntaje: Optional[int], config: Config):
    ancho, alto = landscape(A4)
    centro = ancho / 2
    c.setTitle(f"Certificado {config.entidad}"); c.setAuthor(config.entidad)

    _fondo(c, ancho, alto)

    # Panel crema con doble borde dorado
    x0, y0, x1, y1 = 40, 38, ancho - 40, alto - 62
    c.setFillColor(CREMA); c.roundRect(x0, y0, x1 - x0, y1 - y0, 16, fill=1, stroke=0)
    c.setStrokeColor(ORO); c.setLineWidth(2.2); c.roundRect(x0 + 8, y0 + 8, x1 - x0 - 16, y1 - y0 - 16, 12, fill=0, stroke=1)
    c.setLineWidth(.6); c.roundRect(x0 + 14, y0 + 14, x1 - x0 - 28, y1 - y0 - 28, 9, fill=0, stroke=1)

    # Ramas en las esquinas (por encima del panel)
    _rama(c, x0 + 6, y1 - 8, -40, 120, 6, 26, VERDE_HOJA, .95, curva=.18)
    _rama(c, x0 + 6, y1 - 8, -80, 95, 5, 22, VERDE, .9, curva=-.15)
    _rama(c, x1 - 6, y1 - 8, 220, 120, 6, 26, VERDE_HOJA, .95, curva=-.18)
    _rama(c, x1 - 6, y1 - 8, 260, 95, 5, 22, VERDE, .9, curva=.15)
    _rama(c, x0 + 12, y0 + 12, 82, 78, 4, 18, VERDE_HOJA, .95, curva=-.12)
    _rama(c, x1 - 12, y0 + 12, 98, 78, 4, 18, VERDE_HOJA, .95, curva=.12)

    # Medallón con el logo
    _medallon(c, centro, alto - 62, 50, config.logo)

    # Marca y lema
    ancho_brot = stringWidth("Brot", "Helvetica-Bold", 26)
    ancho_ia = stringWidth("IA", "Helvetica-Bold", 26)
    xm = centro - (ancho_brot + ancho_ia) / 2
    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(VERDE_HOJA); c.drawString(xm, alto - 144, "Brot")
    c.setFillColor(AZUL); c.drawString(xm + ancho_brot, alto - 144, "IA")
    c.setFillColor(ORO)
    _texto_espaciado(c, centro, alto - 160, config.lema.upper(), "Helvetica-Bold", 8, 1.6)

    # Título
    c.setFillColor(VERDE_OSCURO); c.setFont("Times-Bold", 30)
    c.drawCentredString(centro, alto - 199, "CERTIFICADO DE PARTICIPACIÓN")
    # divisor con hoja
    c.setStrokeColor(ORO); c.setLineWidth(1)
    c.line(centro - 150, alto - 217, centro - 14, alto - 217); c.line(centro + 14, alto - 217, centro + 150, alto - 217)
    _hoja(c, centro - 8, alto - 217, 16, 30, ORO, 1, nervadura=False)

    c.setFillColor(GRIS); c.setFont("Times-Italic", 15)
    c.drawCentredString(centro, alto - 236, f"{config.entidad} certifica que")
    c.setFillColor(VERDE_OSCURO); c.setFont("Times-BoldItalic", 32)
    nombre = datos.nombre.upper() if stringWidth(datos.nombre.upper(), "Times-BoldItalic", 32) < 620 else datos.nombre
    c.drawCentredString(centro, alto - 274, nombre)
    c.setStrokeColor(ORO); c.setLineWidth(.8); c.line(centro - 180, alto - 282, centro + 180, alto - 282)
    c.setFillColor(GRIS); c.setFont("Helvetica", 12)
    c.drawCentredString(centro, alto - 300, f"DNI N° {_formatear_dni(datos.dni)}")

    c.setFont("Times-Italic", 15); c.drawCentredString(centro, alto - 326, "completó la capacitación")
    c.setFillColor(VERDE); c.setFont("Times-Bold", 20)
    c.drawCentredString(centro, alto - 351, f"“{config.curso}”")
    c.setFillColor(GRIS); c.setFont("Helvetica", 10.5)
    detalle = "cuatro clases y autoevaluación aprobada"
    if puntaje is not None:
        detalle += f" ({puntaje}%)"
    c.drawCentredString(centro, alto - 371, f"{detalle}  ·  Fecha de emisión: {fecha.strftime('%d/%m/%Y')}")

    # Firmas
    n = len(config.firmantes)
    margen = 105
    paso = (ancho - 2 * margen) / n
    y_linea = 142
    for i, f in enumerate(config.firmantes):
        x = margen + paso * i + paso / 2
        if f.imagen and os.path.exists(f.imagen):
            c.drawImage(f.imagen, x - 72, y_linea + 3, width=144, height=56, mask="auto", preserveAspectRatio=True)
        c.setStrokeColor(VERDE_OSCURO); c.setLineWidth(.8); c.line(x - 78, y_linea, x + 78, y_linea)
        c.setFillColor(VERDE_OSCURO); c.setFont("Helvetica-Bold", 10.5); c.drawCentredString(x, y_linea - 14, f.nombre)
        c.setFillColor(GRIS); c.setFont("Helvetica", 9.5); c.drawCentredString(x, y_linea - 27, f.titulo)

    # Pie
    c.setFont("Helvetica", 7.5); c.setFillColor(GRIS)
    c.drawCentredString(centro, y0 + 42, config.aclaracion)
    c.setFont("Helvetica-Bold", 8); c.setFillColor(VERDE)
    c.drawCentredString(centro, y0 + 27, f"Código de verificación: {codigo}")
    widget = qr.QrCodeWidget(f"BROTIA:{codigo}")
    bx0, by0, bx1, by1 = widget.getBounds()
    tam = 50
    d = Drawing(tam, tam, transform=[tam / (bx1 - bx0), 0, 0, tam / (by1 - by0), 0, 0])
    d.add(widget)
    renderPDF.draw(d, c, x1 - 30 - tam, y0 + 20, 0)


def certificado_bytes(datos: Datos, puntaje: Optional[int] = None, fecha: Optional[date] = None,
                      config: Config = CONFIG, secreto: Optional[str] = None) -> Tuple[bytes, str]:
    """Genera el PDF en memoria (sin tocar el disco). Devuelve (pdf, código)."""
    fecha = fecha or date.today()
    codigo = codigo_verificacion(datos, fecha.isoformat(), config.curso, secreto)
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(A4))
    _dibujar(c, datos, codigo, fecha, puntaje, config)
    c.showPage(); c.save()
    return buf.getvalue(), codigo


def generar_certificado(datos: Datos, carpeta: str = "certificados", puntaje: Optional[int] = None,
                        fecha: Optional[date] = None, config: Config = CONFIG,
                        secreto: Optional[str] = None) -> str:
    """Crea el PDF en disco y devuelve su ruta. El nombre del archivo no incluye datos personales."""
    pdf, codigo = certificado_bytes(datos, puntaje, fecha, config, secreto)
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"certificado_{codigo}.pdf")
    with open(ruta, "wb") as f:
        f.write(pdf)
    return ruta
