from bson import ObjectId
from flask import flash
from config import conexion_mongo
from models.titulares_model import UsuariosTitularesCollection

db = conexion_mongo()

def obtener_titular_por_id(titular_id):
    """
    Obtiene el titular ACTIVO asociado al usuario_rol_id y verifica sus permisos.
    
    Args:
        titular_id (str): ID del titular a buscar

    Returns:
        dict: El titular encontrado o None si no se encuentra o no tiene permisos
    """
    titular = db.titulares.find_one({
        '_id': ObjectId(titular_id),
        'estado_titular': 'activo'
    })
    
    if not titular:
        flash('Titular no encontrado o no tienes permisos para acceder', 'danger')
        return None
    
    return titular

def obtener_titulares_activos(gestor_id):
    '''
    Obtiene los titulares activos para un gestor específico
    '''
    titulares = list(db.usuarios.aggregate([
        {
            "$match": {
                "_id": {"$in": [ObjectId(rel['usuario_id']) for rel in db.usuarios_titulares.find({"gestor_id": ObjectId(gestor_id), "estado": "activo"})]}
            }
        },
        {
            "$lookup": {
                "from": "usuarios_titulares",
                "localField": "_id",
                "foreignField": "usuario_id",
                "as": "titular_info"
            }
        },
        {
            "$unwind": {
                "path": "$titular_info",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$match": {
                "titular_info.gestor_id": ObjectId(gestor_id),
                "titular_info.estado": "activo"
            }
        },
        {
            "$project": {
                "_id": 1,
                "nombre": "$nombre_usuario",
                "alias": "$titular_info.alias"
            }
        },
        {
            "$sort": {
                "alias": 1
            }
        }
    ]))
    
    # Convertir ObjectId a string para cada titular
    for titular in titulares:
        titular['_id'] = str(titular['_id'])
    
    return titulares

