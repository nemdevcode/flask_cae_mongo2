from bson import ObjectId
from config import conexion_mongo

db = conexion_mongo()

def obtener_contrata_por_id(contrata_id):
    return db.contratas.find_one({'_id': ObjectId(contrata_id)})
