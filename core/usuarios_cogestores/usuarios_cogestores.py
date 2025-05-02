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

def usuarios_cogestores_vista():
    '''
    Vista para mostrar los gestores relacionados con el usuario el usuario gestor que los gestiona. 
    Muestra los gestores activos y permite filtrar por la informacion contenida en la variable filtrar_gestor y por estado.
    '''
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas()
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_cogestor_id = resultado
        
        # Obtener parámetros de filtrado
        filtrar_usuario_gestor = request.form.get('filtrar_usuario_gestor', '')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('usuarios_cogestores.usuarios_cogestores'))
        
        # Obtener todos los usuarios con rol de gestor relacionados al usuario cogestor
        usuarios_rol_gestor_id = list(db.usuarios_cogestores.find(
            {'usuario_rol_cogestor_id': usuario_rol_cogestor_id}, 
            {'usuario_rol_gestor_id': 1}
        ))

        # Obtener los usuarios con rol de gestor de la coleccion usuarios_roles
        usuarios_gestores = []
        for usuario_gestor_id in usuarios_rol_gestor_id:
            # Obtener el usuario_rol del gestor
            usuario_rol_gestor = db.usuarios_roles.find_one(
                {'_id': usuario_gestor_id['usuario_rol_gestor_id']}
            )
            if usuario_rol_gestor:
                # Obtener el usuario asociado al rol de gestor
                usuario = db.usuarios.find_one(
                    {'_id': usuario_rol_gestor['usuario_id']}
                )
                if usuario:
                    # Aplicar filtro si existe
                    if filtrar_usuario_gestor:
                        filtro = filtrar_usuario_gestor.lower()
                        if (filtro not in usuario.get('nombre_usuario', '').lower() and
                            filtro not in usuario.get('email', '').lower() and
                            filtro not in usuario.get('telefono_usuario', '').lower()):
                            continue
                    
                    usuarios_gestores.append({
                        'usuario_rol_id': usuario_rol_gestor['_id'],
                        'usuario_id': usuario['_id'],
                        'nombre_usuario': usuario.get('nombre_usuario', ''),
                        'email': usuario.get('email', ''),
                        'telefono_usuario': usuario.get('telefono_usuario', '')
                    })

        return render_template('usuarios/usuarios_cogestores.html',
                               usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                               usuario_cogestor=usuario,
                               usuarios_gestores=usuarios_gestores,
                               filtrar_usuario_gestor=filtrar_usuario_gestor,
                               )
    
    except Exception as e:
        flash(f'Error al cargar la vista de usuarios cogestores: {str(e)}', 'danger')
        return redirect(url_for('usuarios.usuarios'))

def usuarios_cogestores_usuario_gestor_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id):
    '''
    Vista del usuario gestor seleccionado relacionados con el usuario cogestor autenticado.
    '''

    try:
        # Verificar permisos y obtener información
        # permisos_ok, resultado = verificaciones_consultas()
        # if not permisos_ok:
        #     return resultado

        # usuario, usuario_rol_cogestor_id = resultado

        # Obtener el usuario gestor
        usuario_gestor = db.usuarios_roles.find_one(
            {'_id': ObjectId(usuario_rol_gestor_id)}
        )
        if usuario_gestor:
            # Obtener el usuario asociado al rol de gestor
            usuario_gestor = db.usuarios.find_one(
                {'_id': usuario_gestor['usuario_id']}
            )
        else:
            flash('Usuario gestor no encontrado', 'danger')
            return redirect(url_for('usuarios_cogestores.usuarios_cogestores'))
        
        # Obtener parámetros de filtrado
        filtrar_gestor = request.form.get('filtrar_gestor', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('usuarios_cogestores.usuarios_cogestores_usuario_gestor',
                                    usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                    usuario_rol_gestor_id=usuario_rol_gestor_id
                                    ))
        
        # Construir la consulta base - buscar gestores donde el usuario_rol_gestor_id sea el del usuario gestor actual
        consulta_filtros = {'usuario_rol_gestor_id': ObjectId(usuario_rol_gestor_id)}

        # Aplicar filtros si existen
        if filtrar_estado != 'todos':
            consulta_filtros['estado_gestor'] = filtrar_estado
            
        # Obtener los gestores del usuario gestor
        gestores = []
        gestores = list(db.gestores.find(
            consulta_filtros
        ))

        # Si hay filtro por texto, filtrar los gestores
        if filtrar_gestor:
            gestores_filtrados = []
            for gestor in gestores:
                if (filtrar_gestor.lower() in gestor['nombre_gestor'].lower() or
                    filtrar_gestor.lower() in gestor['domicilio'].lower() or
                    filtrar_gestor.lower() in gestor['codigo_postal'].lower() or
                    filtrar_gestor.lower() in gestor['poblacion'].lower() or
                    filtrar_gestor.lower() in gestor['provincia'].lower() or
                    filtrar_gestor.lower() in gestor.get('telefono_gestor', '').lower()):
                    gestores_filtrados.append(gestor)
            gestores = gestores_filtrados

        return render_template('usuarios_cogestores/index.html',
                               usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                               usuario_rol_gestor_id=usuario_rol_gestor_id,
                               usuario_gestor=usuario_gestor,
                               gestores=gestores,
                               filtrar_gestor=filtrar_gestor,
                               filtrar_estado=filtrar_estado
                               )
    except Exception as e:
        flash(f'Error al cargar la vista de uusuario gestor: {str(e)}', 'danger')
        return redirect(url_for('usuarios_cogestores.usuarios_cogestores_usuario_gestor',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id
                                ))
    