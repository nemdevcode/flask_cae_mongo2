from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from utils.usuario_utils import obtener_usuario_autenticado
from utils.rol_utils import obtener_rol, verificar_rol_gestor
from utils.usuario_rol_utils import obtener_usuario_rol
from config import conexion_mongo

db = conexion_mongo()

def usuarios_gestores_vista():
    '''
    Vista para mostrar los gestores relacionados con el usuario autenticado con rol de gestor. 
    Muestra los gestores activos y permite filtrar por la informacion contenida en la variable filtrar_gestor y por estado.
    '''
    try:
        # Obtener usuario autenticado y verificar permisos
        usuario, respuesta_redireccion = obtener_usuario_autenticado()
        if respuesta_redireccion:
            return respuesta_redireccion

        # Verificar rol de gestor
        tiene_rol, usuario_rol_gestor_id = verificar_rol_gestor(usuario['_id'])
        if not tiene_rol:
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        # Obtener parámetros de filtrado
        filtrar_gestor = request.form.get('filtrar_gestor', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('usuarios_gestores.usuarios_gestores'))

        # Obtener todos los gestores relacionados con el usuario_rol_gestor_id
        gestores_relacionados = {
            'usuario_rol_gestor_id': usuario_rol_gestor_id
        }

        # Aplicar filtro por estado si no es 'todos'
        if filtrar_estado != 'todos':
            gestores_relacionados['estado_gestor'] = filtrar_estado

        # Obtener los gestores
        gestores = list(db.gestores.find(gestores_relacionados))

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

def usuarios_gestores_gestor_vista(gestor_id):
    '''
    Vista del gestor seleccionado relacionados con el gestor autenticado.
    '''
    try:
        # Obtener usuario autenticado y verificar permisos
        usuario, respuesta_redireccion = obtener_usuario_autenticado()
        if respuesta_redireccion:
            return respuesta_redireccion
        
        # Verificar rol de gestor
        tiene_rol, usuario_rol_gestor_id = verificar_rol_gestor(usuario['_id'])
        if not tiene_rol:
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        # Verificar que el gestor existe y pertenece al usuario actual
        gestor = db.gestores.find_one({
            '_id': ObjectId(gestor_id),
            'usuario_rol_gestor_id': usuario_rol_gestor_id,
            'estado_gestor': 'activo'
        })
        if not gestor:
            flash('Gestor no encontrado o no tienes permisos para acceder', 'danger')
            return redirect(url_for('usuarios_gestores.usuarios_gestores'))

        return render_template('usuarios_gestores/index.html', 
                               gestor_id=gestor_id,
                               nombre_usuario=usuario.get('nombre_usuario'),
                               nombre_gestor=gestor.get('nombre_gestor')
                               )

    except Exception as e:
        flash(f'Error al cargar la vista del gestor: {str(e)}', 'danger')
        return redirect(url_for('usuarios.usuarios'))

