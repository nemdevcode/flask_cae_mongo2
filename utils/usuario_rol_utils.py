from datetime import datetime
from config import conexion_mongo
from models.usuarios_roles_model import UsuariosRolesCollection
from bson.objectid import ObjectId

db = conexion_mongo()

def obtener_usuario_rol(usuario_id, rol_id):
    """
    Obtiene un usuario_rol por usuario_id y rol_id
    Args:
        usuario_id: ID del usuario
        rol_id: ID del rol
    Retorna:
        - Si existe: (True, usuario_rol_id)
        - Si no existe: (False, None)
    """
    usuario_rol = db.usuarios_roles.find_one({
        'usuario_id': ObjectId(usuario_id),
        'rol_id': ObjectId(rol_id)
    })
    if usuario_rol:
        return True, usuario_rol['_id']
    return False, None

def crear_usuario_rol(usuario_id, rol_id):
    """
    Crea un nuevo usuario_rol
    Args:
        usuario_id: ID del usuario
        rol_id: ID del rol
    Retorna:
        - ID del usuario_rol creado
    """
    fecha_actual = datetime.now()
    usuario_rol = UsuariosRolesCollection(
        usuario_id=usuario_id,
        rol_id=rol_id,
        fecha_activacion=fecha_actual,
        fecha_modificacion=fecha_actual,
        fecha_inactivacion=None,
        estado_usuario_rol='activo'
    )
    resultado_usuario_rol = db.usuarios_roles.insert_one(usuario_rol.__dict__)
    return resultado_usuario_rol.inserted_id

def obtener_roles_usuario(usuario_id):
    """
    Obtiene todos los roles asociados a un usuario
    Args:
        usuario_id: ID del usuario
    Retorna:
        - Lista de roles del usuario
    """
    try:
        # Obtener todas las relaciones usuario-rol del usuario
        usuario_roles = list(db.usuarios_roles.find({
            'usuario_id': ObjectId(usuario_id),
            'estado_usuario_rol': 'activo'
        }))

        # Obtener la información de cada rol
        roles = []
        for usuario_rol in usuario_roles:
            rol = db.roles.find_one({
                '_id': usuario_rol['rol_id'],
                'estado_rol': 'activo'
            })
            if rol:
                roles.append(rol)

        return roles

    except Exception as e:
        print(f'Error al obtener roles del usuario: {str(e)}')
        return [] 