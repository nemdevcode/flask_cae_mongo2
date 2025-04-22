from bson import ObjectId
from config import conexion_mongo
from datetime import datetime
from models.contratas_model import UsuariosContratasCollection

db = conexion_mongo()

def crear_usuario_contrata(usuario_rol_contrata_id, contrata_id, alias):
    """
    Crea un nuevo usuario contratas en la base de datos.
    
    Args:
        usuario_rol_contrata_id (ObjectId): ID del rol de usuario contratas
        contrata_id (str): ID de la contratas a la que pertenece
        alias (str): Alias del usuario contratas
        
    Returns:
        ObjectId: ID del usuario contratas creado
    """
    contrata_data = {
        'usuario_rol_contrata_id': usuario_rol_contrata_id,
        'contrata_id': ObjectId(contrata_id),
        'alias_usuario_contrata': alias,
        'fecha_activacion': datetime.now(),
        'fecha_modificacion': datetime.now(),
        'fecha_inactivacion': None,
        'estado_usuario_contrata': 'activo'
    }
    
    resultado = db.usuarios_contratas.insert_one(contrata_data)
    return resultado.inserted_id

