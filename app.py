from flask import Flask
import os
from routes._routes import rutas
from extensions import init_extensions
from dotenv import load_dotenv, find_dotenv
from config import configurar_email


def crear_app():
    # Forzar recarga del archivo .env, tomaba contraseñas antiguas
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path, override=True)
    app = Flask(__name__)
    # Configuración de MongoDB y clave secreta para las sesiones
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT')

    # Configurar email
    configurar_email(app)
    
    # Inicializar extensiones
    init_extensions(app)

    # Registrar rutas
    rutas(app)

    return app

app = crear_app()

if __name__ == '__main__':
    app.run(debug=True)
