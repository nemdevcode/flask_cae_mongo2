from flask import Flask
import os
from routes._routes import rutas

def crear_app():
    app = Flask(__name__)
    # Configuración de MongoDB y clave secreta para las sesiones
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    rutas(app)

    return app

app = crear_app()

if __name__ == '__main__':
    app.run(debug=True)
