from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from config import conexion_mongo
from utils.usuario_rol_utils import obtener_rol, obtener_usuario_rol

db = conexion_mongo()

def gestores_vista():
    try:
        # Obtener el ID del usuario actual
        usuario_id = session.get('usuario_id')
        
        if not usuario_id:
            flash('No hay usuario autenticado', 'danger')
            return redirect(url_for('login'))

        # Obtener la información del usuario
        usuario = db.usuarios.find_one({'_id': ObjectId(usuario_id)})
        
        if not usuario:
            flash('Usuario no encontrado', 'danger')
            return redirect(url_for('login'))

        # Obtener el rol de gestor
        existe_rol, rol_gestor_id = obtener_rol('gestor')
        
        if not existe_rol:
            flash('Rol de gestor no encontrado', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        # Verificar si el usuario tiene el rol de gestor
        tiene_rol, usuario_rol_id = obtener_usuario_rol(usuario_id, rol_gestor_id)
        
        if not tiene_rol:
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        # Obtener todos los gestores relacionados con el usuario_rol_id
        usuarios_gestores = list(db.usuarios_gestores.find({
            'usuario_rol_id': usuario_rol_id,
            'estado_usuario_gestor': 'activo'
        }))

        # Obtener los datos de los gestores
        gestores = []
        for usuario_gestor in usuarios_gestores:
            gestor = db.gestores.find_one({
                '_id': usuario_gestor['gestor_id'],
                'estado_gestor': 'activo'
            })
            if gestor:
                gestores.append(gestor)

        return render_template('usuarios/usuarios_gestores.html', 
                             nombre_gestor=usuario.get('nombre_usuario'),
                             gestores=gestores)

    except Exception as e:
        flash(f'Error al cargar la vista de gestores: {str(e)}', 'danger')
        return redirect(url_for('usuarios.usuarios'))








