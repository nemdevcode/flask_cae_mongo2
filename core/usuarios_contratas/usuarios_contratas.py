from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from utils.usuario_utils import obtener_usuario_autenticado
from utils.rol_utils import verificar_rol_cogestor
from config import conexion_mongo

db = conexion_mongo()

def verificaciones_consultas():
    '''
    Verifica si el usuario cogestor tiene permisos para acceder a la vista de usuarios cogestores.
    Retorna:
        - (False, respuesta_redireccion) si hay algún error
        - (True, (usuario, usuario_rol_cogestor_id)) si todo está correcto
    '''
    # Obtener usuario autenticado y verificar permisos
    usuario, respuesta_redireccion = obtener_usuario_autenticado()
    if respuesta_redireccion:
        return False, respuesta_redireccion

    # Verificar rol de cogestor
    tiene_rol, usuario_rol_cogestor_id = verificar_rol_cogestor(usuario['_id'])
    if not tiene_rol:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return False, redirect(url_for('usuarios.usuarios'))

    return True, (usuario, usuario_rol_cogestor_id)

def usuarios_contratas_vista():
    pass
