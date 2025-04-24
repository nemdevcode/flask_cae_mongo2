from bson import ObjectId
from config import conexion_mongo
from datetime import datetime
from models.centros_model import UsuariosCentrosCollection

db = conexion_mongo()

def crear_usuario_centro(usuario_rol_centro_id, centro_id, alias):
    """
    Crea un nuevo usuario de centro en la base de datos.
    
    Args:
        usuario_rol_centro_id (ObjectId): ID del rol de usuario de centro
        centro_id (str): ID del centro a la que pertenece
        alias (str): Alias del usuario de centro
        
    Returns:
        ObjectId: ID del usuario de centro creado
    """
    centro_data = {
        'usuario_rol_centro_id': usuario_rol_centro_id,
        'centro_id': ObjectId(centro_id),
        'alias_usuario_centro': alias,
        'fecha_activacion': datetime.now(),
        'fecha_modificacion': datetime.now(),
        'fecha_inactivacion': None,
        'estado_usuario_centro': 'activo'
    }
    
    resultado = db.usuarios_centros.insert_one(centro_data)
    return resultado.inserted_id