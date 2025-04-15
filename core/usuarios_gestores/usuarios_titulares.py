from flask import render_template, request, redirect, url_for, session, flash
from bson import ObjectId
from datetime import datetime
from utils.usuario_utils import (
    crear_usuario,
    verificar_usuario_existente,
    obtener_usuario_autenticado
)
from utils.rol_utils import (
    obtener_rol, 
    crear_rol,
    verificar_rol_gestor
)
from utils.usuario_rol_utils import (
    obtener_usuario_rol, 
    crear_usuario_rol
)
from utils.gestor_utils import obtener_gestor_por_usuario
from utils.titular_utils import obtener_titular_por_id
from utils.usuario_titular_utils import crear_usuario_titular
from utils.token_utils import generar_token_verificacion
from utils.email_utils import enviar_email
from config import conexion_mongo

db = conexion_mongo()

def verificaciones_consultas(gestor_id, titular_id):
    '''
    Función auxiliar para verificar permisos de gestor y obtener información necesaria
    Retorna:
        - (False, respuesta_redireccion) si hay algún error
        - (True, (usuario, usuario_rol_id, gestor, titular)) si todo está correcto
    '''
    # Obtener usuario autenticado y verificar permisos
    usuario, respuesta_redireccion = obtener_usuario_autenticado()
    if respuesta_redireccion:
        return False, respuesta_redireccion

    # Verificar rol de gestor
    tiene_rol, usuario_rol_id = verificar_rol_gestor(usuario['_id'])
    if not tiene_rol:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return False, redirect(url_for('usuarios.usuarios'))

    # Obtener el gestor asociado al usuario_rol_id
    gestor = obtener_gestor_por_usuario(gestor_id, usuario_rol_id)
    if not gestor:
        flash('Gestor no encontrado o no tienes permisos para acceder', 'danger')
        return False, redirect(url_for('usuarios_gestores.usuarios_gestores_gestor', gestor_id=gestor_id))

    # Obtener la información del titular
    titular = obtener_titular_por_id(titular_id)
    if not titular:
        flash('Titular no encontrado', 'danger')
        return False, redirect(url_for('ug_titulares.titulares_titular', gestor_id=gestor_id, titular_id=titular_id))

    return True, (usuario, usuario_rol_id, gestor, titular)

def usuarios_titulares_vista(gestor_id, titular_id):
    '''
    Vista para listar los usuarios titulares del titular seleccionado
    '''
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id)
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_id, gestor, titular = resultado
        nombre_gestor = gestor.get('nombre_gestor', 'Gestor')

        # Obtener los usuarios titulares asociados al titular_id
        usuarios_titulares = []
        usuarios_titulares_cursor = db.usuarios_titulares.find({'titular_id': ObjectId(titular_id)})
        
        # Obtener el rol de titular
        existe_rol, rol_titular_id = obtener_rol('titular')
        if not existe_rol:
            flash('Rol de titular no encontrado', 'danger')
            return redirect(url_for('ug_titulares.titulares_titular', gestor_id=gestor_id, titular_id=titular_id))
        
        for ut in usuarios_titulares_cursor:
            # Obtener el usuario_rol del titular usando la función obtener_usuario_rol
            usuario_rol = db.usuarios_roles.find_one({'_id': ut['usuario_rol_titular_id']})
            
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

        return render_template('usuarios_gestores/usuarios_titulares/listar.html',
                               usuarios_titulares=usuarios_titulares,
                               titular_id=titular_id,
                               gestor_id=gestor_id,
                               nombre_gestor=nombre_gestor,
                               titular=titular
                            )

    except Exception as e:
        flash(f'Error al listar los usuarios titulares: {str(e)}', 'danger')
        return redirect(url_for('ug_titulares.titulares_titular', gestor_id=gestor_id, titular_id=titular_id))

def usuarios_titulares_crear_vista(gestor_id, titular_id):
    '''
    Vista para crear un nuevo usuario titular del titular seleccionado
    '''
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id)
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_id, gestor, titular = resultado
        nombre_gestor = gestor.get('nombre_gestor', 'Gestor')

        if request.method == 'GET':
            return render_template('usuarios_gestores/usuarios_titulares/crear.html',
                                    nombre_gestor=nombre_gestor,
                                    titular=titular,
                                    gestor_id=gestor_id)

        if request.method == 'POST':
            # Obtener datos del formulario
            email = request.form.get('email', '').strip().lower()
            alias = request.form.get('alias', '').strip().upper()

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
                crear_usuario_titular(usuario_rol_titular_id, titular_id, alias)
                flash('Este email ya está registrado, será asignado como usuario titular para este titular', 'success')
                return redirect(url_for('ug_usuarios_titulares.usuarios_titulares', gestor_id=gestor_id, titular_id=titular_id))

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
            crear_usuario_titular(usuario_rol_titular_id, titular_id, alias)

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

            return redirect(url_for('ug_usuarios_titulares.usuarios_titulares', gestor_id=gestor_id, titular_id=titular_id))

    except Exception as e:
        flash(f'Error al crear el usuario titular: {str(e)}', 'danger')
        return render_template('usuarios_gestores/usuarios_titulares/crear.html',
                             form_data=request.form,
                             nombre_gestor=nombre_gestor,
                             titular=titular,
                             gestor_id=gestor_id)

def usuarios_titulares_actualizar_vista(gestor_id, titular_id, usuario_titular_id):
    '''
    Vista para actualizar un usuario titular del titular seleccionado
    '''
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id)
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_id, gestor, titular = resultado
        nombre_gestor = gestor.get('nombre_gestor', 'Gestor')

        # Obtener el usuario titular a actualizar
        usuario_titular = db.usuarios_titulares.find_one({'_id': ObjectId(usuario_titular_id)})
        if not usuario_titular:
            flash('Usuario titular no encontrado', 'danger')
            return redirect(url_for('ug_usuarios_titulares.usuarios_titulares', gestor_id=gestor_id, titular_id=titular_id))

        # Obtener el usuario_rol del titular
        usuario_rol = db.usuarios_roles.find_one({'_id': usuario_titular['usuario_rol_titular_id']})
        if not usuario_rol:
            flash('Usuario rol no encontrado', 'danger')
            return redirect(url_for('ug_usuarios_titulares.usuarios_titulares', gestor_id=gestor_id, titular_id=titular_id))

        # Obtener la información del usuario titular
        usuario = db.usuarios.find_one({'_id': ObjectId(usuario_rol['usuario_id'])})
        if not usuario:
            flash('Usuario no encontrado', 'danger')
            return redirect(url_for('ug_usuarios_titulares.usuarios_titulares', gestor_id=gestor_id, titular_id=titular_id))

        # Preparar la información del usuario titular en el formato que espera el template
        usuario_titular_info = {
            '_id': usuario_titular['_id'],
            'titular_info': {
                'alias': usuario_titular['alias_usuario_titular'],
                'estado_usuario_titular': usuario_titular['estado_usuario_titular']
            },
            'email': usuario['email']
        }

        if request.method == 'GET':
            return render_template('usuarios_gestores/usuarios_titulares/actualizar.html',
                                usuario_titular=usuario_titular_info,
                                titular=titular,
                                gestor_id=gestor_id,
                                titular_id=titular_id)

        if request.method == 'POST':
            # Obtener datos del formulario
            alias = request.form.get('alias', '').strip().upper()
            estado_usuario_titular = request.form.get('estado_usuario_titular', 'activo')

            # Actualizar el usuario titular
            db.usuarios_titulares.update_one(
                {'_id': ObjectId(usuario_titular_id)},
                {
                    '$set': {
                        'alias_usuario_titular': alias,
                        'estado_usuario_titular': estado_usuario_titular
                    }
                }
            )

            flash('Usuario titular actualizado correctamente', 'success')
            return redirect(url_for('ug_usuarios_titulares.usuarios_titulares', gestor_id=gestor_id, titular_id=titular_id))

    except Exception as e:
        flash(f'Error al actualizar el usuario titular: {str(e)}', 'danger')
        return redirect(url_for('ug_usuarios_titulares.usuarios_titulares', gestor_id=gestor_id, titular_id=titular_id))

def usuarios_titulares_eliminar_vista(gestor_id, titular_id, usuario_titular_id):
    '''
    Vista para eliminar un usuario titular del titular seleccionado
    '''
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id)
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_id, gestor, titular = resultado

        # Obtener el usuario titular a eliminar
        usuario_titular = db.usuarios_titulares.find_one({'_id': ObjectId(usuario_titular_id)})
        if not usuario_titular:
            flash('Usuario titular no encontrado', 'danger')
            return redirect(url_for('ug_usuarios_titulares.usuarios_titulares', gestor_id=gestor_id, titular_id=titular_id))

        # Eliminar el usuario titular
        result = db.usuarios_titulares.delete_one({'_id': ObjectId(usuario_titular_id)})

        if result.deleted_count > 0:
            flash('Usuario titular eliminado exitosamente', 'success')
            return redirect(url_for('ug_usuarios_titulares.usuarios_titulares', 
                                 gestor_id=gestor_id, 
                                 titular_id=titular_id))
        else:
            flash('No se pudo eliminar el usuario titular', 'danger')
            return redirect(url_for('ug_usuarios_titulares.usuarios_titulares', 
                                 gestor_id=gestor_id, 
                                 titular_id=titular_id))

    except Exception as e:
        flash(f'Error al eliminar el usuario titular: {str(e)}', 'danger')
        return redirect(url_for('ug_usuarios_titulares.usuarios_titulares', gestor_id=gestor_id, titular_id=titular_id))
