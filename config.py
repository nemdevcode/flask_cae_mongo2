from dotenv import load_dotenv
import os
from pymongo import MongoClient
import certifi
from icecream import ic

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

def configurar_email(app):
    """Configura las opciones de email en la aplicación Flask"""
    # Obtener y verificar la contraseña
    mail_password = os.getenv('MAIL_PASSWORD')
    ic("Variables de entorno disponibles:", os.environ.keys())
    ic("Contraseña del .env:", mail_password)
    
    # Configuración de Flask-Mail para Gmail
    app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False,
        MAIL_USERNAME='cae.accesible@gmail.com',
        MAIL_PASSWORD=mail_password,
        MAIL_DEFAULT_SENDER='cae.accesible@gmail.com',
        MAIL_MAX_EMAILS=None,
        MAIL_ASCII_ATTACHMENTS=False,
        MAIL_DEBUG=True
    )

    # Verificar la configuración final
    ic("Configuración final:")
    ic("Username:", app.config['MAIL_USERNAME'])
    ic("Password configurada:", app.config['MAIL_PASSWORD'])






