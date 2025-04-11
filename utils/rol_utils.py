from datetime import datetime
from models.roles_model import RolesCollection
from config import conexion_mongo

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
