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

