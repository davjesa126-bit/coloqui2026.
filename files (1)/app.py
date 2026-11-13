"""Interfaz web de BrotIA (Flask). Ejecutar: flask --app web.app run

Sin estado en el servidor: el historial del chat lo guarda el navegador y los datos personales
del certificado se usan solo para generar el PDF en memoria (no se guardan ni se registran).
"""
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
import io

from brotia import capacitacion
from brotia.agente import Agente
from brotia.certificado import certificado_bytes
from brotia.config import CONFIG
from brotia.privacidad import AVISO, Datos, normalizar_dni, normalizar_nombre

RAIZ = Path(__file__).resolve().parent.parent


def _cargar_env() -> None:
    env = RAIZ / ".env"
    if env.exists():
        for linea in env.read_text(encoding="utf-8").splitlines():
            if "=" in linea and not linea.startswith("#"):
                k, v = linea.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def create_app() -> Flask:
    _cargar_env()
    app = Flask(__name__, static_folder=str(RAIZ / "assets"), static_url_path="/assets")
    app.config["MAX_CONTENT_LENGTH"] = 32 * 1024  # evita cuerpos enormes

    @app.after_request
    def cabeceras(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["Referrer-Policy"] = "no-referrer"
        return resp

    @app.get("/")
    def inicio():
        return render_template("index.html", config=CONFIG)

    @app.get("/capacitacion")
    def pagina_capacitacion():
        return render_template("capacitacion.html", config=CONFIG, clases=capacitacion.CLASES,
                               preguntas=capacitacion.PREGUNTAS, aviso=AVISO)

    @app.post("/api/chat")
    def chat():
        cuerpo = request.get_json(silent=True) or {}
        mensaje = str(cuerpo.get("mensaje", "")).strip()[:2000]
        if not mensaje:
            return jsonify(error="Escribí un mensaje."), 400
        historial = []
        for m in (cuerpo.get("historial") or [])[-20:]:
            if isinstance(m, dict) and m.get("role") in ("user", "assistant") and isinstance(m.get("content"), str):
                historial.append({"role": m["role"], "content": m["content"][:4000]})
        agente = Agente()
        agente.historial = historial
        return jsonify(respuesta=agente.responder(mensaje))

    def _evaluar(cuerpo):
        r = cuerpo.get("respuestas")
        if not isinstance(r, list) or not all(isinstance(i, int) for i in r):
            return None
        try:
            return capacitacion.evaluar(r)
        except ValueError:
            return None

    @app.post("/api/evaluar")
    def evaluar():
        res = _evaluar(request.get_json(silent=True) or {})
        if res is None:
            return jsonify(error="Respuestas inválidas."), 400
        return jsonify(puntaje=res[0], aprobado=res[1], nota_minima=CONFIG.nota_minima)

    @app.post("/api/certificado")
    def certificado():
        cuerpo = request.get_json(silent=True) or {}
        if cuerpo.get("acepto") is not True:
            return jsonify(error="Sin tu consentimiento no se emite el certificado."), 400
        res = _evaluar(cuerpo)
        if res is None or not res[1]:
            return jsonify(error="La autoevaluación no está aprobada."), 400
        nombre = normalizar_nombre(str(cuerpo.get("nombre", "")))
        dni = normalizar_dni(str(cuerpo.get("dni", "")))
        if not nombre or not dni:
            return jsonify(error="Revisá nombre y apellido y el DNI (7 u 8 números)."), 400
        pdf, codigo = certificado_bytes(Datos(nombre, dni), puntaje=res[0])
        resp = send_file(io.BytesIO(pdf), mimetype="application/pdf", as_attachment=True,
                         download_name=f"certificado_{codigo}.pdf")
        resp.headers["Cache-Control"] = "no-store"
        return resp

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=False)
