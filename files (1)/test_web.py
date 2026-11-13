import os
import unittest

os.environ["BROTIA_SECRET"] = "clave-de-prueba"
os.environ.pop("ANTHROPIC_API_KEY", None)

from brotia import capacitacion
from web.app import create_app


class TestWeb(unittest.TestCase):
    def setUp(self):
        self.c = create_app().test_client()
        self.ok = [p.correcta for p in capacitacion.PREGUNTAS]

    def test_paginas(self):
        self.assertEqual(self.c.get("/").status_code, 200)
        r = self.c.get("/capacitacion")
        self.assertEqual(r.status_code, 200)
        self.assertIn("AVISO SOBRE TUS DATOS PERSONALES".encode(), r.data)
        self.assertEqual(self.c.get("/assets/logo.png").status_code, 200)

    def test_evaluar(self):
        j = self.c.post("/api/evaluar", json={"respuestas": self.ok}).get_json()
        self.assertTrue(j["aprobado"])

    def test_certificado_requiere_consentimiento(self):
        r = self.c.post("/api/certificado", json={"respuestas": self.ok, "acepto": False,
                                                   "nombre": "Ana Pérez", "dni": "12345678"})
        self.assertEqual(r.status_code, 400)

    def test_certificado_requiere_aprobar(self):
        malas = [(q.correcta + 1) % len(q.opciones) for q in capacitacion.PREGUNTAS]
        r = self.c.post("/api/certificado", json={"respuestas": malas, "acepto": True,
                                                   "nombre": "Ana Pérez", "dni": "12345678"})
        self.assertEqual(r.status_code, 400)

    def test_certificado_ok(self):
        r = self.c.post("/api/certificado", json={"respuestas": self.ok, "acepto": True,
                                                   "nombre": "Ana Pérez", "dni": "12.345.678"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data[:4], b"%PDF")
        self.assertEqual(r.headers["Cache-Control"], "no-store")

    def test_chat_sin_clave(self):
        j = self.c.post("/api/chat", json={"mensaje": "hola"}).get_json()
        # Sin clave o sin el paquete 'anthropic', responde con un aviso en vez de fallar
        self.assertTrue("ANTHROPIC_API_KEY" in j["respuesta"] or "anthropic" in j["respuesta"])


if __name__ == "__main__":
    unittest.main()
