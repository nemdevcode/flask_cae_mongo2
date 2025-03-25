from dotenv import load_dotenv
import os
from pymongo import MongoClient
import certifi

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')

SECRET_KEY = os.getenv('SECRET_KEY')

# Configuración del servidor de correo
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT = int(os.getenv('MAIL_PORT'))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') == 'True'
MAIL_USE_SSL = os.getenv('MAIL_USE_SSL') == 'True'
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME') 

def conexion_mongo():
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        base_datos = client['flask_cae']
        return base_datos
    except Exception as e:
        print(f"Error al conectar con MongoDB: {e}")
        return None






