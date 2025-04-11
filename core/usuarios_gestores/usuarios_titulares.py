from flask import render_template, request, redirect, url_for, session, flash
from bson import ObjectId
from datetime import datetime
from utils.usuario_utils import (
    crear_usuario,
    verificar_usuario_existente
)
from utils.rol_utils import (
    obtener_rol, 
    crear_rol
)
from utils.usuario_rol_utils import (
    obtener_usuario_rol, 
    crear_usuario_rol
)
from utils.token_utils import generar_token_verificacion
from utils.email_utils import enviar_email
from config import conexion_mongo

db = conexion_mongo()

def usuarios_titulares_vista(titular_id):
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
        gestor_id = str(gestor['_id'])

        # Obtener los usuarios titulares asociados al titular_id
        usuarios_titulares = []
        usuarios_titulares_cursor = db.usuarios_titulares.find({'titular_id': ObjectId(titular_id)})
        
        for ut in usuarios_titulares_cursor:
            # Obtener el usuario_rol del titular usando usuario_rol_titular_id
            usuario_rol = db.usuarios_roles.find_one({'_id': ObjectId(ut['usuario_rol_titular_id'])})
            
            if usuario_rol:
                # Obtener la información del usuario titular
                usuario_titular = db.usuarios.find_one({'_id': ObjectId(usuario_rol['usuario_id'])})
                
                if usuario_titular:
                    titular_info = {
                        '_id': ut['_id'],
                        'titular_info': {
                            'alias': ut['alias_usuario_titular'],
                            'estado_usuario_titular': ut['estado_usuario_titular']
                        },
                        'email': usuario_titular['email'],
                        'nombre_usuario': usuario_titular.get('nombre_usuario', '')
                    }
                    usuarios_titulares.append(titular_info)
        
        # Obtener la información del titular
        titular = db.titulares.find_one({'_id': ObjectId(titular_id)})
        if not titular:
            flash('Titular no encontrado', 'danger')
            return redirect(url_for('gestores.gestores_titulares', gestor_id=gestor_id))

        return render_template(
            'usuarios_gestores/usuarios_titulares/listar.html',
            usuarios_titulares=usuarios_titulares,
            titular_id=titular_id,
            gestor_id=gestor_id,
            nombre_gestor=nombre_gestor,
            titular=titular
        )

    except Exception as e:
        flash(f'Error al listar los usuarios titulares: {str(e)}', 'danger')
        return redirect(url_for('login'))

def usuarios_titulares_crear_vista(gestor_id, titular_id):
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
            return redirect(url_for('gestores.gestores_titulares', gestor_id=gestor_id))

        if request.method == 'GET':
            return render_template('usuarios_gestores/usuarios_titulares/crear.html',
                                 nombre_gestor=nombre_gestor,
                                 titular=titular,
                                 gestor_id=gestor_id)

        if request.method == 'POST':
            # Obtener datos del formulario
            email = request.form.get('email', '').strip().lower()
            alias = request.form.get('alias', '').strip().upper()
            
            if not email or not alias:
                flash('El email y el alias son obligatorios', 'danger')
                return render_template('usuarios_gestores/usuarios_titulares/crear.html',
                                     form_data=request.form,
                                     nombre_gestor=nombre_gestor,
                                     titular=titular,
                                     gestor_id=gestor_id)

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
                                            titular=titular,
                                            gestor_id=gestor_id)
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
                return redirect(url_for('gestores.gestores_usuarios_titulares', gestor_id=gestor_id, titular_id=titular_id))

            # Si el usuario no existe, crear nuevo usuario y usuario titular
            # Generar token de verificación
            token = generar_token_verificacion(email)
            
            # Crear diccionario con los datos del nuevo usuario
            datos_usuario = {
                'token_verificacion': token,
                'verificado': False,
                'estado_usuario': 'pendiente'
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

            return redirect(url_for('gestores.gestores_usuarios_titulares', gestor_id=gestor_id, titular_id=titular_id))

    except Exception as e:
        flash(f'Error al crear el usuario titular: {str(e)}', 'danger')
        return render_template('usuarios_gestores/usuarios_titulares/crear.html',
                             form_data=request.form,
                             nombre_gestor=nombre_gestor,
                             titular=titular,
                             gestor_id=gestor_id)

def usuarios_titulares_actualizar_vista(titular_id):
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

def usuarios_titulares_eliminar_vista(titular_id):
    
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