from bson import ObjectId
from config import conexion_mongo
from datetime import datetime
from models.titulares_model import UsuariosTitularesCollection

db = conexion_mongo()

def crear_usuario_titular(usuario_rol_titular_id, titular_id, alias):
    """
    Crea un nuevo usuario titular en la base de datos.
    
    Args:
        usuario_rol_titular_id (ObjectId): ID del rol de usuario titular
        titular_id (str): ID del titular al que pertenece
        alias (str): Alias del usuario titular
        
    Returns:
        ObjectId: ID del usuario titular creado
    """
    titular_data = {
        'usuario_rol_titular_id': usuario_rol_titular_id,
        'titular_id': ObjectId(titular_id),
        'alias_usuario_titular': alias,
        'fecha_activacion': datetime.now(),
        'fecha_modificacion': datetime.now(),
        'fecha_inactivacion': None,
        'estado_usuario_titular': 'activo'
    }
    
    resultado = db.usuarios_titulares.insert_one(titular_data)
    return resultado.inserted_id

