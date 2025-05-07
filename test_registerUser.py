import unittest                 # Librería para pruebas unitarias
import os                      # Librería para manejar archivos del sistema
from json import dumps         # Para convertir diccionarios a texto JSON
from users import registerUser # Se importa la función a probar desde users.py

class TestRegisterUser(unittest.TestCase):  # Clase que agrupa las pruebas unitarias de registro

    def test_registro_nuevo_usuario(self):
        # Verifica si el archivo "users.txt" existe; si no, lo crea vacío
        if not os.path.exists("users.txt"):
            open("users.txt", "w").close()

        # Abre el archivo para leer los usuarios ya registrados
        with open("users.txt", "r") as f:
            usuarios = f.readlines()

        # Verifica si ya existe un usuario con ID predeterminado
        ya_existe = any('"id": 1001' in usuario for usuario in usuarios)

        if not ya_existe:
            # Si no está registrado, intenta registrarlo y verifica el mensaje validación
            resultado = registerUser("1001", "clave123", "Ingeniería", "student")
            self.assertEqual(resultado, "User succesfully registered")
        else:
            # Si ya está registrado, simplemente verifica que el mensaje sea el correcto
            resultado = registerUser("1001", "clave123", "Ingeniería", "student")
            self.assertEqual(resultado, "User already registered")

    def test_usuario_ya_registrado(self):
        # Verifica si el archivo "users.txt" existe, si no existe, lo crea vacío
        if not os.path.exists("users.txt"):
            open("users.txt", "w").close()

        # Abre el archivo para revisar si el usuario con ID predeterminado ya existe
        with open("users.txt", "r") as f:
            usuarios = f.readlines()

        ya_existe = any('"id": 2002' in usuario for usuario in usuarios)

        # Si el usuario no existe, lo agrega manualmente al archivo con un diccionario 
        if not ya_existe:
            with open("users.txt", "a") as f:
                datos = {"id": 2002, "password": "clave2002", "program": "Derecho", "role": "professor"}
                f.write(dumps(datos) + "\n")

        # Intenta registrarlo de nuevo, donde se espera que retorne mensaje de ya registrado
        resultado = registerUser("2002", "clave2002", "Derecho", "professor")
        self.assertEqual(resultado, "User already registered")

# Este bloque permite que las pruebas se ejecuten al correr en este archivo directamente
if __name__ == "__main__":
    unittest.main()
