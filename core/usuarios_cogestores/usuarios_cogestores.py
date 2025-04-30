from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from utils.usuario_utils import obtener_usuario_autenticado
from utils.rol_utils import verificar_rol_cogestor
from config import conexion_mongo

db = conexion_mongo()

def usuarios_cogestores_vista():
    '''
    Vista para mostrar los gestores relacionados con el usuario el usuario gestor que los gestiona. 
    Muestra los gestores activos y permite filtrar por la informacion contenida en la variable filtrar_gestor y por estado.
    '''
    try:
        # Obtener usuario autenticado y verificar permisos
        usuario, respuesta_redireccion = obtener_usuario_autenticado()
        if respuesta_redireccion:
            return respuesta_redireccion
        
        # Verificar rol de cogestor
        tiene_rol, usuario_rol_cogestor_id = verificar_rol_cogestor(usuario['_id'])
        if not tiene_rol:
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('usuarios.usuarios'))
        
        # Obtener el usuario_rol_gestor_id usuario cogestor autenticado
        usuario_rol_gestor_id = db.usuarios_cogestores.find_one({'usuario_rol_cogestor_id': usuario_rol_cogestor_id})
        print(f"usuario_rol_gestor_id: {usuario_rol_gestor_id}")

        # Obtener los gestores con usuario_rol_gestor_id
        gestores = db.gestores.find({'usuario_rol_gestor_id': usuario_rol_gestor_id})
        print(f"gestores: {gestores}")
        

        return render_template('usuarios/usuarios_cogestores.html',
                               gestores=gestores,
                               usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                               usuario_rol_gestor_id=usuario_rol_gestor_id
                               )
    
    except Exception as e:
        flash(f'Error al cargar la vista de usuarios cogestores: {str(e)}', 'danger')
        return redirect(url_for('usuarios.usuarios'))

def usuarios_cogestores_gestor_vista(usuario_rol_id, usuario_rol_gestor_id, gestor_id):
    '''
    Vista del gestor seleccionado relacionados con el usuario cogestor autenticado.
    '''
    pass