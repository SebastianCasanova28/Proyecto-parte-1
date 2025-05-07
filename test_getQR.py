import unittest
import os
import io
from json import dumps
from users import registerUser, getQR

class TestGetQR(unittest.TestCase):

    def test_getqr_usuario_existente(self):
        # Crear usuario si no existe
        if not os.path.exists("users.txt"):
            open("users.txt", "w").close()

        with open("users.txt", "r") as f:
            usuarios = f.readlines()

        ya_existe = any('"id": 4004' in usuario for usuario in usuarios)
        if not ya_existe:
            with open("users.txt", "a") as f:
                datos = {"id": 4004, "password": "clave4004", "program": "Psicología", "role": "student"}
                f.write(dumps(datos) + "\n")

        # Prueba que el QR se genere correctamente
        resultado = getQR("4004", "clave4004")
        self.assertIsInstance(resultado, io.BytesIO)
        self.assertNotEqual(resultado.getvalue(), b'')

    def test_getqr_usuario_no_existente(self):
        # Prueba con usuario que no existe
        resultado = getQR("9999", "clave_invalida")
        self.assertIsInstance(resultado, io.BytesIO)
        self.assertEqual(resultado.getvalue(), b'')

    def test_getqr_contraseña_incorrecta(self):
        # Prueba con contraseña incorrecta para un ID válido
        resultado = getQR("4004", "clave_incorrecta")
        self.assertIsInstance(resultado, io.BytesIO)
        self.assertEqual(resultado.getvalue(), b'')

if __name__ == "__main__":
    unittest.main()
