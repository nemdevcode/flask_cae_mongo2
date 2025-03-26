from flask import render_template, session, redirect, url_for, flash
from bson.objectid import ObjectId
from models.usuarios_model import UsuariosCollection
from models.roles_model import RolesCollection
from models.usuarios_roles_model import UsuariosRolesCollection

from config import conexion_mongo

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
        rol_gestor = db.roles.find_one({'nombre_rol': 'gestor'})
        if not rol_gestor:
            flash('Rol de gestor no encontrado', 'danger')
            return redirect(url_for('usuarios.usuarios'))
            
        rol_gestor_id = rol_gestor['_id']

        # Verificar si el usuario tiene el rol de gestor
        usuario_rol = db.usuarios_roles.find_one({
            'usuario_id': ObjectId(usuario_id),
            'rol_id': rol_gestor_id
        })
        
        if not usuario_rol:
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        return render_template('gestores/index.html', 
                             nombre_gestor=usuario.get('nombre_usuario'))

    except Exception as e:
        flash(f'Error al cargar la vista de gestores: {str(e)}', 'danger')
        return redirect(url_for('usuarios.usuarios'))








