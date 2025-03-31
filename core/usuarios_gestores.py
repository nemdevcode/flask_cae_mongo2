from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from config import conexion_mongo
from utils.usuario_rol_utils import obtener_rol, obtener_usuario_rol
from datetime import datetime

db = conexion_mongo()

def usuarios_gestores_vista():
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

        # Obtener parámetros de filtrado
        filtrar_gestor = request.form.get('filtrar_gestor', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('gestores.usuarios_gestores'))

        # Obtener todos los gestores relacionados con el usuario_rol_id
        query = {
            'usuario_rol_id': usuario_rol_id,
            'estado_gestor': 'activo'
        }

        # Aplicar filtro por estado si no es 'todos'
        if filtrar_estado != 'todos':
            query['estado_gestor'] = filtrar_estado

        # Obtener los gestores
        gestores = list(db.gestores.find(query))

        # Filtrar por texto si se especifica
        if filtrar_gestor:
            gestores = [
                gestor for gestor in gestores
                if (filtrar_gestor.lower() in gestor['nombre_gestor'].lower() or
                    filtrar_gestor.lower() in gestor['cif_dni'].lower() or
                    filtrar_gestor.lower() in gestor['domicilio'].lower() or
                    filtrar_gestor.lower() in gestor['codigo_postal'].lower() or
                    filtrar_gestor.lower() in gestor['poblacion'].lower() or
                    filtrar_gestor.lower() in gestor['provincia'].lower() or
                    filtrar_gestor.lower() in gestor['telefono_gestor'].lower())
            ]

        return render_template('usuarios/usuarios_gestores.html', 
                             nombre_gestor=usuario.get('nombre_usuario'),
                             gestores=gestores,
                             filtrar_gestor=filtrar_gestor,
                             filtrar_estado=filtrar_estado)

    except Exception as e:
        flash(f'Error al cargar la vista de gestores: {str(e)}', 'danger')
        return redirect(url_for('usuarios.usuarios'))

def usuarios_gestores_eliminar_vista():
    pass





