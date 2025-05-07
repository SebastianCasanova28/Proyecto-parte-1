# Estos son los paquetes que se deben instalar
# pip install pycryptodome
# pip install pyqrcode
# pip install pypng
# pip install pyzbar
# pip install pillow

# No modificar estos módulos que se importan
from pyzbar.pyzbar import decode
from PIL import Image
from json import dumps
from json import loads
from hashlib import sha256
from Crypto.Cipher import AES
import base64
import pyqrcode
from os import urandom
import io
from datetime import datetime
import cv2

# Nombre del archivo con la base de datos de usuarios
usersFileName="users.txt"

# Fecha actual
date=None
# Clave aleatoria para encriptar el texto de los códigos QR
key=None

# Función para encriptar (no modificar)
def encrypt_AES_GCM(msg, secretKey):
    aesCipher = AES.new(secretKey, AES.MODE_GCM)
    ciphertext, authTag = aesCipher.encrypt_and_digest(msg)
    return (ciphertext, aesCipher.nonce, authTag)

# Función para desencriptar (no modificar)
def decrypt_AES_GCM(encryptedMsg, secretKey):
    (ciphertext, nonce, authTag) = encryptedMsg
    aesCipher = AES.new(secretKey, AES.MODE_GCM, nonce)
    plaintext = aesCipher.decrypt_and_verify(ciphertext, authTag)
    return plaintext

# Función que genera un código QR (no modificar)
def generateQR(id,program,role,buffer):
    # Variables globales para la clave y la fecha
    global key
    global date

    # Información que irá en el código QR, antes de encriptar
    data={'id': id, 'program':program,'role':role}
    datas=dumps(data).encode("utf-8")

    # Si no se ha asignado una clave se genera
    if key is None:
        key =urandom(32) 
        # Se almacena la fecha actual
        date=datetime.today().strftime('%Y-%m-%d')
    
    # Si cambió la fecha actual se genera una nueva clave y 
    # se actualiza la fecha
    if date !=datetime.today().strftime('%Y-%m-%d'):
        key =urandom(32) 
        date=datetime.today().strftime('%Y-%m-%d')

    # Se encripta la información
    encrypted = list(encrypt_AES_GCM(datas,key))

    # Se crea un JSON convirtiendo los datos encriptados a base64 para poder usar texto en el QR
    qr_text=dumps({'qr_text0':base64.b64encode(encrypted[0]).decode('ascii'),
                                'qr_text1':base64.b64encode(encrypted[1]).decode('ascii'),
                                'qr_text2':base64.b64encode(encrypted[2]).decode('ascii')})
    
    # Se crea el código QR a partir del JSON
    qrcode = pyqrcode.create(qr_text)

    # Se genera una imagen PNG que se escribe en el buffer                    
    qrcode.png(buffer,scale=8)          


# Se debe codificar esta función
# Argumentos: id (entero), password (cadena), program (cadena) y role (cadena)
# Si el usuario ya existe deber retornar  "User already registered"
# Si el usuario no existe debe registar el usuario en la base de datos y retornar  "User succesfully registered"   

def registerUser(id, password, program, role):
    
    reconocimiento = open("users.txt", "r")
    usuarios = reconocimiento.readlines()
    reconocimiento.close()

    
    for i in usuarios:
        datos = loads(i)
       
        if datos["id"] == int(id):
            return "User already registered"
    
    
    nueva_linea = {"id": int(id),"password": password,"program": program,"role": role}

    reconocimiento = open("users.txt", "a")
    reconocimiento.write(dumps(nueva_linea) + "\n")
    reconocimiento.close()

    return "User succesfully registered"

           
#Se debe complementar esta función
# Función que genera el código QR
# retorna el código QR si el id y la contraseña son correctos (usuario registrado)
# Ayuda (debe usar la función generateQR)                   

def getQR(id, password):
    
    buffer = io.BytesIO()    
   
    reconocimiento = open("users.txt", "r")
    usuarios = reconocimiento.readlines()
    reconocimiento.close()

    for i in usuarios:
        datos = loads(i)
        if datos["id"] == int(id) and datos["password"] == password:
                                
            generateQR(id, datos["program"], datos["role"], buffer)
            
            return buffer

    return buffer
        


# Se debe complementar esta función
# Función que recibe el código QR como PNG
# debe verificar si el QR contiene datos que pueden ser desencriptados con la clave (key), y si el usuario está registrado
# Debe asignar un puesto de parqueadero dentro de los disponibles.

# Puestos de parqueo
def sendQR(png):
    from pyzbar.pyzbar import decode
    from PIL import Image
    import cv2
    import numpy as np

    puestos = [
        ((455,  19), (539, 129)),  # Profesor 1
        ((378,  19), (458, 129)),  # Profesor 2
        ((295,  19), (377, 129)),  # Profesor 3
        ((212,  19), (293, 129)),  # Estudiante 1
        ((128,  19), (211, 129)),  # Estudiante 2
        ((37,   19), (125, 129)),  # Estudiante 3
        ((464, 230), (540, 343)),  # Otros 1
        ((375, 230), (464, 342)),  # Otros 2
        ((293, 230), (373, 338)),  # Otros 3
    ]

    roles_puestos = {
        "professor": range(0, 3),
        "student": range(3, 6),
        "otros": range(6, 9)
    }

    umbral = 30

    def contornos(area):
        gris = cv2.cvtColor(area, cv2.COLOR_BGR2GRAY)
        bordes = cv2.Canny(gris, 100, 200)
        contorno, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return len(contorno)

    try:
        # Decodificar el QR
        decodedQR = decode(Image.open(io.BytesIO(png)))[0].data.decode('ascii')
        data = loads(decodedQR)

        # Desencriptar datos
        decrypted = loads(decrypt_AES_GCM(
            (base64.b64decode(data["qr_text0"]),base64.b64decode(data["qr_text1"]),base64.b64decode(data["qr_text2"])),key))

        id_persona = decrypted["id"]
        rol_persona = decrypted["role"].lower()  #Convertido a minúscula

        # Leer usuarios
        with open("users.txt", "r") as f:
            usuarios = f.readlines()

        for i in usuarios:
            datos = loads(i)
            if datos["id"] == int(id_persona):
                
                rol = rol_persona if rol_persona in roles_puestos else "otros"

                # Abrir cámara IP
                video = cv2.VideoCapture("http://192.168.20.49:8080/video")
                ret, frame = video.read()
                video.release()

                if not ret:
                    return "Error accediendo a la cámara"

                # Buscar puesto libre
                for i in roles_puestos.get(rol, []):
                    area = frame[puestos[i][0][1]:puestos[i][1][1], puestos[i][0][0]:puestos[i][1][0]]
                    if contornos(area) < umbral:
                        return f"Puesto {i + 1} asignado al {rol}"

                return f"No hay puestos disponibles para el rol: {rol}"

        return "User not registered"

    except Exception as e:
        return "Invalid QR or decryption failed"

