from bson import ObjectId
from config import conexion_mongo

db = conexion_mongo()

def obtener_centros(titular_id):
    '''
    Obtiene los centros activos para un titular específico
    '''
    centros = list(db.centros.find({"titular_id": ObjectId(titular_id)}))
    # Convertir ObjectId a string para cada centro
    for centro in centros:
        centro['_id'] = str(centro['_id'])
        centro['titular_id'] = str(centro['titular_id'])
    return centros
