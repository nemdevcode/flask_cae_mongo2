from datetime import datetime
from config import conexion_mongo
from models.roles_model import RolesCollection
from models.usuarios_roles_model import UsuariosRolesCollection
from models.usuarios_model import UsuariosCollection
from bson.objectid import ObjectId

db = conexion_mongo()

def obtener_rol(nombre_rol):
    """
    Obtiene un rol por su nombre, creándolo si no existe
    Args:
        nombre_rol: Nombre del rol a buscar
    Retorna:
        - Si existe: (True, rol_id)
        - Si no existe: (False, None)
    """
    rol = db.roles.find_one({'nombre_rol': nombre_rol})
    if rol:
        return True, rol['_id']
    return False, None

def crear_rol(nombre_rol):
    """
    Crea un nuevo rol
    Args:
        nombre_rol: Nombre del rol a crear
    Retorna:
        - ID del rol creado
    """
    fecha_actual = datetime.now()
    rol = RolesCollection(
        nombre_rol=nombre_rol,
        descripcion=f'Rol de {nombre_rol}',
        fecha_activacion=fecha_actual,
        fecha_modificacion=fecha_actual,
        fecha_inactivacion=None,
        estado_rol='activo'
    )
    resultado_rol = db.roles.insert_one(rol.__dict__)
    return resultado_rol.inserted_id

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

def verificar_usuario_existente(email):
    """
    Verifica si un usuario existe por su email
    Args:
        email: Email del usuario a verificar
    Retorna:
        - Si existe: (True, usuario_id)
        - Si no existe: (False, None)
    """
    usuario = db.usuarios.find_one({'email': email})
    if usuario:
        return True, usuario['_id']
    return False, None

def crear_usuario(email, datos_usuario):
    """
    Crea un nuevo usuario
    Args:
        email: Email del usuario
        datos_usuario: Diccionario con los datos del usuario
    Retorna:
        - ID del usuario creado
    """
    fecha_actual = datetime.now()
    usuario = UsuariosCollection(
        email=email,
        fecha_activacion=fecha_actual,
        fecha_modificacion=fecha_actual,
        fecha_inactivacion=None,
        estado_usuario='pendiente',
        **datos_usuario
    )
    resultado_usuario = db.usuarios.insert_one(usuario.__dict__)
    return resultado_usuario.inserted_id 