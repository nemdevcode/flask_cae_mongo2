from flask import session, redirect, url_for, flash
from bson.objectid import ObjectId
from config import conexion_mongo
from datetime import datetime
from models.usuarios_model import UsuariosCollection


db = conexion_mongo()

def obtener_usuario_autenticado():
    """
    Verifica y obtiene el usuario autenticado.
    Retorna:
        - Si hay error: (None, respuesta_redireccion)
        - Si todo está bien: (usuario, None)
    """
    try:
        # Obtener el ID del usuario actual
        usuario_id = session.get('usuario_id')
        
        if not usuario_id:
            flash('No hay usuario autenticado', 'danger')
            return None, redirect(url_for('login'))

        # Obtener la información del usuario
        usuario = db.usuarios.find_one({'_id': ObjectId(usuario_id)})
        
        if not usuario:
            flash('Usuario no encontrado', 'danger')
            return None, redirect(url_for('login'))

        return usuario, None

    except Exception as e:
        flash(f'Error al verificar el usuario: {str(e)}', 'danger')
        return None, redirect(url_for('login')) 
        
def crear_usuario(email, datos_usuario):
    """
    Crea un nuevo usuario
    Args:
        email: Email del usuario
        datos_usuario: Diccionario con datos adicionales del usuario
    Retorna:
        - ID del usuario creado
    """
    fecha_actual = datetime.now()
    
    # Asegurar que los campos requeridos estén presentes
    if 'nombre_usuario' not in datos_usuario:
        datos_usuario['nombre_usuario'] = email.split('@')[0]  # Usar la parte local del email como nombre
    if 'telefono_usuario' not in datos_usuario:
        datos_usuario['telefono_usuario'] = ''  # Telefono vacío por defecto
    
    usuario = UsuariosCollection(
        email=email,
        **datos_usuario,
        fecha_activacion=fecha_actual,
        fecha_modificacion=fecha_actual,
        fecha_inactivacion=None
    )
    resultado_usuario = db.usuarios.insert_one(usuario.__dict__)
    return resultado_usuario.inserted_id

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