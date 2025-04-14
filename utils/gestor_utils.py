from bson import ObjectId
from flask import flash
from config import conexion_mongo

db = conexion_mongo()

def obtener_gestor_por_usuario(gestor_id, usuario_rol_id):
    """
    Obtiene el gestor ACTIVO asociado al usuario_rol_id y verifica sus permisos.
    
    Args:
        gestor_id (str): ID del gestor a buscar
        usuario_rol_id (ObjectId): ID del rol de usuario
        
    Returns:
        dict: El gestor encontrado o None si no se encuentra o no tiene permisos
    """
    gestor = db.gestores.find_one({
        '_id': ObjectId(gestor_id),
        'usuario_rol_id': usuario_rol_id,
        'estado_gestor': 'activo'
    })
    
    if not gestor:
        flash('Gestor no encontrado o no tienes permisos para acceder', 'danger')
        return None
        
    return gestor
