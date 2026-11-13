import os
import tempfile
import unittest
from datetime import date
from unittest import mock

from brotia import capacitacion
from brotia.certificado import codigo_verificacion, generar_certificado, verificar
from brotia.privacidad import Datos, normalizar_dni, normalizar_nombre, pedir_datos

SECRETO = "clave-de-prueba"


class TestPrivacidad(unittest.TestCase):
    def test_dni(self):
        self.assertEqual(normalizar_dni("12.345.678"), "12345678")
        self.assertIsNone(normalizar_dni("123"))
        self.assertIsNone(normalizar_dni("abc"))

    def test_nombre(self):
        self.assertEqual(normalizar_nombre("  Ana   Pérez "), "Ana Pérez")
        self.assertIsNone(normalizar_nombre("Ana"))

    def test_rechazo_no_pide_datos(self):
        pedidos = []
        def entrada(p):
            pedidos.append(p)
            return "n"
        self.assertIsNone(pedir_datos(entrada, lambda *_: None))
        self.assertEqual(len(pedidos), 1)  # solo la pregunta de consentimiento

    def test_aceptacion(self):
        resp = iter(["s", "Ana Pérez", "12.345.678"])
        datos = pedir_datos(lambda p: next(resp), lambda *_: None)
        self.assertEqual((datos.nombre, datos.dni), ("Ana Pérez", "12345678"))

    def test_repr_oculta_dni(self):
        self.assertNotIn("12345678", repr(Datos("Ana Pérez", "12345678")))


class TestCertificado(unittest.TestCase):
    def setUp(self):
        self.datos = Datos("Ana Pérez", "12345678")

    def test_codigo_estable_y_verificable(self):
        c1 = codigo_verificacion(self.datos, "2026-11-11", "Curso", SECRETO)
        c2 = codigo_verificacion(self.datos, "2026-11-11", "Curso", SECRETO)
        self.assertEqual(c1, c2)
        self.assertTrue(verificar(self.datos, "2026-11-11", c1, "Curso", SECRETO))
        self.assertFalse(verificar(Datos("Otra Persona", "12345678"), "2026-11-11", c1, "Curso", SECRETO))

    def test_pdf_generado_sin_dni_en_nombre_de_archivo(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = generar_certificado(self.datos, tmp, 88, date(2026, 11, 11), secreto=SECRETO)
            self.assertTrue(os.path.exists(ruta))
            self.assertNotIn("12345678", os.path.basename(ruta))
            self.assertEqual(open(ruta, "rb").read(4), b"%PDF")

    def test_sin_secreto_falla(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                codigo_verificacion(self.datos, "2026-11-11", "Curso")


class TestCapacitacion(unittest.TestCase):
    def test_todas_correctas_aprueba(self):
        p, ok = capacitacion.evaluar([q.correcta for q in capacitacion.PREGUNTAS])
        self.assertEqual((p, ok), (100, True))

    def test_todas_incorrectas_reprueba(self):
        malas = [(q.correcta + 1) % len(q.opciones) for q in capacitacion.PREGUNTAS]
        self.assertFalse(capacitacion.evaluar(malas)[1])


if __name__ == "__main__":
    unittest.main()
