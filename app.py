from flask import Flask
import os
from routes._routes import rutas
from extensions import init_extensions
from icecream import ic
from dotenv import load_dotenv, find_dotenv

def crear_app():
    # Forzar recarga del archivo .env
    dotenv_path = find_dotenv()
    ic("Archivo .env encontrado en:", dotenv_path)
    load_dotenv(dotenv_path, override=True)
    
    # Obtener y verificar la contraseña
    mail_password = os.getenv('MAIL_PASSWORD')
    ic("Variables de entorno disponibles:", os.environ.keys())
    ic("Contraseña del .env:", mail_password)
    
    app = Flask(__name__)
    # Configuración de MongoDB y clave secreta para las sesiones
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT')

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
    
    # Inicializar extensiones
    init_extensions(app)

    # Registrar rutas
    rutas(app)

    return app

app = crear_app()

if __name__ == '__main__':
    app.run(debug=True)
