from flask import render_template, request, redirect, url_for, session, flash
from bson import ObjectId
from datetime import datetime
from config import conexion_mongo
from utils.usuario_rol_utils import (
    obtener_rol, 
    obtener_usuario_rol, 
    crear_usuario, 
    crear_usuario_rol, 
    verificar_usuario_existente,
    crear_rol
)
from utils.token_utils import generar_token_verificacion
from utils.email_utils import enviar_email

db = conexion_mongo()

def gestores_usuarios_titulares_vista(titular_id):
    try:
        # Obtener el ID del usuario actual
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            flash('No hay usuario autenticado', 'danger')
            return redirect(url_for('login'))

        # Obtener el rol de gestor
        existe_rol, rol_gestor_id = obtener_rol('gestor')
        if not existe_rol:
            flash('Rol de gestor no encontrado', 'danger')
            return redirect(url_for('login'))

        # Verificar si el usuario tiene el rol de gestor
        tiene_rol, usuario_rol_id = obtener_usuario_rol(usuario_id, rol_gestor_id)
        if not tiene_rol:
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('login'))

        # Obtener el gestor asociado al usuario_rol_id
        gestor = db.gestores.find_one({'usuario_rol_id': ObjectId(usuario_rol_id)})
        if not gestor:
            flash('Gestor no encontrado', 'danger')
            return redirect(url_for('login'))

        # Obtener la información del usuario
        usuario = db.usuarios.find_one({'_id': ObjectId(usuario_id)})
        if not usuario:
            flash('Usuario no encontrado', 'danger')
            return redirect(url_for('login'))

        nombre_gestor = usuario.get('nombre_usuario', 'Gestor')

        # Obtener el titular
        titular = db.titulares.find_one({'_id': ObjectId(titular_id)})
        if not titular:
            flash('Titular no encontrado', 'danger')
            return redirect(url_for('gestores.gestores_titulares'))

        # Obtener parámetros de filtrado
        filtrar_titular = request.form.get('filtrar_titular', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('gestores.gestores_usuarios_titulares', titular_id=titular_id))

        # Construir la consulta base - buscar usuarios titulares donde el titular_id sea el del titular actual
        query = {'titular_id': ObjectId(titular_id)}
        
        # Aplicar filtros si existen
        if filtrar_estado != 'todos':
            query['estado_usuario_titular'] = filtrar_estado

        # Obtener los usuarios titulares asociados al titular
        usuarios_titulares = []
        usuarios_titulares_cursor = db.usuarios_titulares.find(query)
        
        for ut in usuarios_titulares_cursor:
            # Obtener la información del usuario titular
            usuario_rol_titular = db.usuarios_roles.find_one({'_id': ut['usuario_rol_titular_id']})
            if usuario_rol_titular:
                usuario_titular = db.usuarios.find_one({'_id': usuario_rol_titular['usuario_id']})
                if usuario_titular:
                    # Si hay filtro por nombre, verificar si coincide
                    if filtrar_titular:
                        if (filtrar_titular.lower() not in usuario_titular['email'].lower() and 
                            filtrar_titular.lower() not in ut['alias_usuario_titular'].lower()):
                            continue

                    usuarios_titulares.append({
                        '_id': ut['_id'],
                        'alias_usuario_titular': ut['alias_usuario_titular'],
                        'email': usuario_titular['email'],
                        'nombre_usuario': usuario_titular.get('nombre_usuario', ''),
                        'estado_usuario_titular': ut['estado_usuario_titular']
                    })

        return render_template('usuarios_gestores/usuarios_titulares/listar.html', 
                             usuarios_titulares=usuarios_titulares,
                             nombre_gestor=nombre_gestor,
                             filtrar_titular=filtrar_titular,
                             filtrar_estado=filtrar_estado,
                             titular_id=titular_id)

    except Exception as e:
        flash(f'Error al listar los usuarios titulares: {str(e)}', 'danger')
        return redirect(url_for('login'))

def gestores_usuarios_titulares_crear_vista(titular_id):
    try:
        # Obtener el ID del usuario actual
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            flash('No hay usuario autenticado', 'danger')
            return redirect(url_for('login'))

        # Obtener el rol de gestor
        existe_rol, rol_gestor_id = obtener_rol('gestor')
        if not existe_rol:
            flash('Rol de gestor no encontrado', 'danger')
            return redirect(url_for('login'))

        # Verificar si el usuario tiene el rol de gestor
        tiene_rol, usuario_rol_id = obtener_usuario_rol(usuario_id, rol_gestor_id)
        if not tiene_rol:
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('login'))

        # Obtener el gestor asociado al usuario_rol_id
        gestor = db.gestores.find_one({'usuario_rol_id': ObjectId(usuario_rol_id)})
        if not gestor:
            flash('Gestor no encontrado', 'danger')
            return redirect(url_for('login'))

        # Obtener la información del usuario
        usuario = db.usuarios.find_one({'_id': ObjectId(usuario_id)})
        if not usuario:
            flash('Usuario no encontrado', 'danger')
            return redirect(url_for('login'))

        nombre_gestor = usuario.get('nombre_usuario', 'Gestor')

        # Obtener el titular
        titular = db.titulares.find_one({'_id': ObjectId(titular_id)})
        if not titular:
            flash('Titular no encontrado', 'danger')
            return redirect(url_for('gestores.gestores_titulares'))

        if request.method == 'GET':
            return render_template('usuarios_gestores/usuarios_titulares/crear.html',
                                 nombre_gestor=nombre_gestor,
                                 titular=titular)

        if request.method == 'POST':
            # Obtener datos del formulario
            email = request.form.get('email', '').strip().lower()
            alias = request.form.get('alias', '').strip().upper()
            
            if not email or not alias:
                flash('El email y el alias son obligatorios', 'danger')
                return render_template('usuarios_gestores/usuarios_titulares/crear.html',
                                     form_data=request.form,
                                     nombre_gestor=nombre_gestor,
                                     titular=titular)

            # Verificar si el usuario existe
            existe_usuario, usuario_titular_id = verificar_usuario_existente(email)
            
            if existe_usuario:
                # Obtener rol de titular
                existe_rol, rol_titular_id = obtener_rol('titular')
                
                if not existe_rol:
                    rol_titular_id = crear_rol('titular')
                
                # Verificar si el usuario ya tiene el rol de titular
                tiene_rol_titular, usuario_rol_titular_id = obtener_usuario_rol(usuario_titular_id, rol_titular_id)
                
                if tiene_rol_titular:
                    # Verificar si ya es usuario titular para este titular específico
                    titular_existente = db.usuarios_titulares.find_one({
                        'usuario_rol_titular_id': usuario_rol_titular_id,
                        'titular_id': ObjectId(titular_id)
                    })
                    
                    if titular_existente:
                        flash('Este email ya está registrado como usuario titular para este titular', 'danger')
                        return render_template('usuarios_gestores/usuarios_titulares/crear.html',
                                            form_data=request.form,
                                            nombre_gestor=nombre_gestor,
                                            titular=titular)
                else:
                    # Si no tiene el rol de titular, crearlo
                    usuario_rol_titular_id = crear_usuario_rol(usuario_titular_id, rol_titular_id)
                
                # Crear el usuario titular
                titular_data = {
                    'usuario_rol_titular_id': usuario_rol_titular_id,
                    'titular_id': ObjectId(titular_id),
                    'alias_usuario_titular': alias,
                    'fecha_activacion': datetime.now(),
                    'fecha_modificacion': datetime.now(),
                    'fecha_inactivacion': None,
                    'estado_usuario_titular': 'activo'
                }
                db.usuarios_titulares.insert_one(titular_data)
                flash('Este email ya está registrado, será asignado como usuario titular para este titular', 'success')
                return redirect(url_for('gestores.gestores_usuarios_titulares'))

            # Si el usuario no existe, crear nuevo usuario y usuario titular
            # Generar token de verificación
            token = generar_token_verificacion(email)
            
            # Crear diccionario con los datos del nuevo usuario
            datos_usuario = {
                'token_verificacion': token,
                'verificado': False
            }
            
            # Crear el nuevo usuario
            nuevo_usuario_id = crear_usuario(email, datos_usuario)
            
            # Obtener rol de titular y crear usuario_rol
            existe_rol, rol_titular_id = obtener_rol('titular')
            if not existe_rol:
                rol_titular_id = crear_rol('titular')
            
            usuario_rol_titular_id = crear_usuario_rol(nuevo_usuario_id, rol_titular_id)
            
            # Crear el usuario titular
            titular_data = {
                'usuario_rol_titular_id': usuario_rol_titular_id,
                'titular_id': ObjectId(titular_id),
                'alias_usuario_titular': alias,
                'fecha_activacion': datetime.now(),
                'fecha_modificacion': datetime.now(),
                'fecha_inactivacion': None,
                'estado_usuario_titular': 'activo'
            }
            db.usuarios_titulares.insert_one(titular_data)

            # Enviar email de verificación solo para usuarios nuevos
            link_verificacion = url_for('verificar_email', token=token, email=email, _external=True)
            cuerpo_email = render_template(
                    'emails/registro_titular.html',
                    alias=alias,
                    link_verificacion=link_verificacion
                )

            if enviar_email(email, "Activación de cuenta - CAE Accesible", cuerpo_email):
                flash('Usuario titular creado correctamente. Se ha enviado un email de activación.', 'success')
            else:
                flash('Usuario titular creado pero hubo un error al enviar el email de activación.', 'warning')

            return redirect(url_for('gestores.gestores_usuarios_titulares'))

    except Exception as e:
        flash(f'Error al crear el usuario titular: {str(e)}', 'danger')
        return render_template('usuarios_gestores/usuarios_titulares/crear.html',
                             form_data=request.form,
                             nombre_gestor=nombre_gestor,
                             titular=titular)

def gestores_usuarios_titulares_actualizar_vista(titular_id):
    try:
        # Obtener el ID del usuario actual
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            flash('No hay usuario autenticado', 'danger')
            return redirect(url_for('login'))

        # Obtener el rol de gestor
        existe_rol, rol_gestor_id = obtener_rol('gestor')
        if not existe_rol:
            flash('Rol de gestor no encontrado', 'danger')
            return redirect(url_for('login'))

        # Verificar si el usuario tiene el rol de gestor
        tiene_rol, usuario_rol_id = obtener_usuario_rol(usuario_id, rol_gestor_id)
        if not tiene_rol:
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('login'))

        # Obtener el gestor asociado al usuario_rol_id
        gestor = db.gestores.find_one({'usuario_rol_id': ObjectId(usuario_rol_id)})
        if not gestor:
            flash('Gestor no encontrado', 'danger')
            return redirect(url_for('login'))

        # Obtener la información del usuario
        usuario = db.usuarios.find_one({'_id': ObjectId(usuario_id)})
        if not usuario:
            flash('Usuario no encontrado', 'danger')
            return redirect(url_for('login'))

        nombre_gestor = usuario.get('nombre_usuario', 'Gestor')

        # Obtener el usuario titular
        usuario_titular = db.usuarios_titulares.find_one({'_id': ObjectId(titular_id)})
        if not usuario_titular:
            flash('Usuario titular no encontrado', 'danger')
            return redirect(url_for('gestores.gestores_titulares'))

        # Obtener la información del usuario
        usuario_info = db.usuarios.find_one({'_id': usuario_titular['usuario_id']})
        if not usuario_info:
            flash('Información del usuario no encontrada', 'danger')
            return redirect(url_for('gestores.gestores_titulares'))

        # Obtener el titular
        titular = db.titulares.find_one({'_id': usuario_titular['titular_id']})
        if not titular:
            flash('Titular no encontrado', 'danger')
            return redirect(url_for('gestores.gestores_titulares'))

        if request.method == 'GET':
            return render_template('usuarios_gestores/usuarios_titulares/actualizar.html',
                                 usuario_titular=usuario_titular,
                                 usuario_info=usuario_info,
                                 nombre_gestor=nombre_gestor,
                                 titular=titular)

        if request.method == 'POST':
            # Obtener datos del formulario
            alias = request.form.get('alias', '').strip().upper()
            estado = request.form.get('estado', 'inactivo')
            
            if not alias:
                flash('El alias es obligatorio', 'danger')
                return render_template('usuarios_gestores/usuarios_titulares/actualizar.html',
                                     usuario_titular=usuario_titular,
                                     usuario_info=usuario_info,
                                     nombre_gestor=nombre_gestor,
                                     titular=titular)

            # Actualizar el usuario titular
            result = db.usuarios_titulares.update_one(
                {'_id': ObjectId(titular_id)},
                {
                    '$set': {
                        'alias_usuario_titular': alias,
                        'estado_usuario_titular': estado,
                        'fecha_modificacion': datetime.now()
                    }
                }
            )

            if result.modified_count > 0:
                flash('Usuario titular actualizado exitosamente', 'success')
                return redirect(url_for('gestores.gestores_titulares', titular_id=titular['_id']))
            else:
                flash('No se realizaron cambios en el usuario titular', 'info')
                return redirect(url_for('gestores.gestores_titulares', titular_id=titular['_id']))

    except Exception as e:
        flash(f'Error al actualizar el usuario titular: {str(e)}', 'danger')
        return redirect(url_for('gestores.gestores_titulares'))

def gestores_usuarios_titulares_eliminar_vista(titular_id):
    
    try:
        # Obtener el ID del gestor actual
        gestor_id = session.get('usuario_id')
        if not gestor_id:
            flash('No hay gestor autenticado', 'danger')
            return redirect(url_for('login'))

        # Obtener el ID del titular a eliminar
        titular_id = request.args.get('titular_id')
        if not titular_id:
            flash('ID de titular no proporcionado', 'danger')
            return redirect(url_for('gestores.gestores_usuarios_titulares'))

        # Verificar que el titular pertenece al gestor actual
        titular = db.usuarios_titulares.find_one({
            '_id': ObjectId(titular_id),
            'gestor_id': ObjectId(gestor_id)
        })

        if not titular:
            flash('Titular no encontrado o no pertenece a este gestor', 'danger')
            return redirect(url_for('gestores.gestores_usuarios_titulares'))

        # Eliminar el titular
        db.usuarios_titulares.delete_one({'_id': ObjectId(titular_id)})
        flash('Titular eliminado exitosamente', 'success')
        return redirect(url_for('gestores.gestores_usuarios_titulares'))

    except Exception as e:
        flash(f'Error al eliminar el titular: {str(e)}', 'danger')
        return redirect(url_for('gestores.gestores_usuarios_titulares'))

def usuarios_titulares_vista():
    return render_template('usuarios_titulares.html')

def usuarios_titulares_gestor_vista():
    return render_template('usuarios_titulares_gestor.html')