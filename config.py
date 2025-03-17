from dotenv import load_dotenv
import os
from pymongo import MongoClient
import certifi

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')

SECRET_KEY = os.getenv('SECRET_KEY')

def conexion_mongo():
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        base_datos = client['flask_cae']
        return base_datos
    except Exception as e:
        print(f"Error al conectar con MongoDB: {e}")
        return None






