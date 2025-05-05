from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from utils.usuario_utils import verificar_usuario_existente, crear_usuario
from utils.rol_utils import obtener_rol, crear_rol, obtener_usuario_rol
from utils.usuario_rol_utils import crear_usuario_rol
from utils.token_utils import generar_token_verificacion
from utils.email_utils import enviar_email
from config import conexion_mongo

db = conexion_mongo()

def usuarios_titulares_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    '''
    Vista para mostrar los usuarios titulares de un titular
    '''
    try:
        # Obtener nombre del titular
        nombre_titular = db.titulares.find_one({'_id': ObjectId(titular_id)})['nombre_titular']

        # Obtener parámetros de filtrado
        filtrar_usuario_titular = request.form.get('filtrar_usuario_titular', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('uc_usuarios_titulares.usuarios_titulares', 
                                    usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                    usuario_rol_gestor_id=usuario_rol_gestor_id,
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id
                                    ))
        
        # Construir la consulta base - buscar usuarios titulares donde el titular_id sea el del titular actual
        query = {'titular_id': ObjectId(titular_id)}
        
        # Aplicar filtros si existen
        if filtrar_usuario_titular:
            query['alias_usuario_titular'] = {'$regex': filtrar_usuario_titular, '$options': 'i'}

        if filtrar_estado != 'todos':
            query['estado_usuario_titular'] = filtrar_estado
        

        # Obtener los usuarios titulares asociados al titular_id
        usuarios_titulares = []
        usuarios_titulares_cursor = db.usuarios_titulares.find(query)

        for ut in usuarios_titulares_cursor:
            # Obtener el usuario_rol del titular usando la función obtener_usuario_rol
            usuario_rol_titular = db.usuarios_roles.find_one({'_id': ut['usuario_rol_titular_id']})
            
            if usuario_rol_titular:
                # Obtener la información del usuario titular
                usuario_titular = db.usuarios.find_one({'_id': ObjectId(usuario_rol_titular['usuario_id'])})
                
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

        return render_template('usuarios_cogestores/usuarios_titulares/listar.html',
                            usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                            usuario_rol_gestor_id=usuario_rol_gestor_id, 
                            gestor_id=gestor_id, 
                            titular_id=titular_id,
                            nombre_titular=nombre_titular,
                            usuarios_titulares=usuarios_titulares
                            )
    except Exception as e:
        flash(f'Error al listar los usuarios titulares: {str(e)}', 'danger')
        return redirect(url_for('uc_usuarios_titulares.usuarios_titulares', 
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id, 
                                titular_id=titular_id
                                ))

def crear_usuario_titular(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, datos_formulario):
    '''
    Función para crear un usuario titular
    '''
    try:
        # Obtener los datos del formulario
        email = datos_formulario.get('email', '').strip().lower()
        alias = datos_formulario.get('alias', '').strip().upper()

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
                        return False, {
                            'email': email,
                            'alias': alias
                        }
                    
                else:
                    # Si no tiene el rol de titular, crearlo
                    usuario_rol_titular_id = crear_usuario_rol(usuario_titular_id, rol_titular_id)
        
        # Obtener rol de titular
        existe_rol, rol_titular_id = obtener_rol('titular')
        
        if not existe_rol:
            rol_titular_id = crear_rol('titular')

        # Verificar si el usuario ya tiene el rol de titular
        tiene_rol_titular, usuario_rol_titular_id = obtener_usuario_rol(usuario_titular_id, rol_titular_id)
        
        if tiene_rol_titular:
            # Insertar el usuario titular en la base de datos
            insert = db.usuarios_titulares.insert_one({
                'usuario_rol_titular_id': ObjectId(usuario_rol_titular_id),
                'titular_id': ObjectId(titular_id),
                'alias_usuario_titular': alias,
                'estado_usuario_titular': 'activo'
            })
            flash('Este email ya está registrado se ha creado un usuario titular para este titular', 'info')
            return True, None
        
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

        # Insertar el usuario titular en la base de datos
        insert = db.usuarios_titulares.insert_one({
            'usuario_rol_titular_id': ObjectId(usuario_rol_titular_id),
            'titular_id': ObjectId(titular_id),
            'alias_usuario_titular': alias,
            'estado_usuario_titular': 'activo'
        })

        # Enviar email de verificación solo para usuarios nuevos
        link_verificacion = url_for('verificar_email', 
                                    token=token, 
                                    email=email, 
                                    _external=True
                                    )
        cuerpo_email = render_template('emails/registro_titular.html',
                                        alias=alias,
                                        link_verificacion=link_verificacion
                                        )

        if enviar_email(email, "Activación de cuenta - CAE Accesible", cuerpo_email):
            # flash('Usuario titular creado correctamente. Se ha enviado un email de activación.', 'success')
            if insert.inserted_id:
                flash('Usuario titular creado correctamente. Se ha enviado un email de activación.', 'success')
                return True, None
            else:
                flash('Error al crear el usuario titular', 'danger')
                return False, datos_formulario
        else:
            flash('Usuario titular creado pero hubo un error al enviar el email de activación.', 'warning')

        
    except Exception as e:
        flash(f'Error al crear el usuario titular: {str(e)}', 'danger')
        return False, datos_formulario

def usuarios_titulares_crear_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    '''
    Vista para crear un usuario titular
    '''
    try:
        if request.method == 'GET':
            datos_formulario = {}
            return render_template('usuarios_cogestores/usuarios_titulares/crear.html',
                                    usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                                    usuario_rol_gestor_id=usuario_rol_gestor_id, 
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id,
                                    datos_formulario=datos_formulario
                                    )
        
        if request.method == 'POST':
            # Crear usuario titular
            creado, datos_formulario = crear_usuario_titular(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, request.form)
            if creado:
                return redirect(url_for('uc_usuarios_titulares.usuarios_titulares', 
                                        usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                        usuario_rol_gestor_id=usuario_rol_gestor_id,
                                        gestor_id=gestor_id, 
                                        titular_id=titular_id
                                        ))
            else:
                return render_template('usuarios_cogestores/usuarios_titulares/crear.html',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id,
                                datos_formulario=datos_formulario
                                )

    except Exception as e:
        flash(f'Error al crear el usuario titular: {str(e)}', 'danger')
        return redirect(url_for('uc_usuarios_titulares.usuarios_titulares', 
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id, 
                                titular_id=titular_id
                                ))

def actualizar_usuario_titular(usuario_titular_id, datos_formulario):
    '''
    Función para actualizar un usuario titular
    '''
    try:
        # Obtener los datos del formulario
        alias = datos_formulario.get('alias', '').strip().upper()
        estado_usuario_titular = datos_formulario.get('estado_usuario_titular', 'activo')

        # Actualizar el usuario titular
        actualizar = db.usuarios_titulares.update_one(
            {'_id': ObjectId(usuario_titular_id)},
            {'$set': {
                'alias_usuario_titular': alias,
                'estado_usuario_titular': estado_usuario_titular
            }}
        )

        if actualizar.modified_count > 0:
            flash('Usuario titular actualizado exitosamente', 'success')
            return True, None
        else:
            flash('No se realizaron cambios en el usuario titular', 'info')
            return True, None

    except Exception as e:
        flash(f'Error al actualizar el usuario titular: {str(e)}', 'danger')
        return False, datos_formulario

def usuarios_titulares_actualizar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, usuario_titular_id):
    '''
    Vista para actualizar un usuario titular
    '''
    try:
        # Obtener el usuario titular a actualizar
        usuario_titular = db.usuarios_titulares.find_one({'_id': ObjectId(usuario_titular_id)})
        # Obtener el usuario_rol del titular
        usuario_rol = db.usuarios_roles.find_one({'_id': usuario_titular['usuario_rol_titular_id']})
         # Obtener la información del usuario titular
        usuario = db.usuarios.find_one({'_id': ObjectId(usuario_rol['usuario_id'])})
        # Preparar la información del usuario titular en el formato que espera el template
        usuario_titular_info = {
            '_id': usuario_titular['_id'],
            'titular_info': {
                'alias': usuario_titular['alias_usuario_titular'],
                'estado_usuario_titular': usuario_titular['estado_usuario_titular']
            },
            'email': usuario['email']
        }

        # Si es una petición POST, procesar el formulario
        if request.method == 'POST':
            actualizar = actualizar_usuario_titular(usuario_titular_id, request.form)
            if actualizar:
                return redirect(url_for('uc_usuarios_titulares.usuarios_titulares', 
                                        usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                        usuario_rol_gestor_id=usuario_rol_gestor_id,
                                        gestor_id=gestor_id, 
                                        titular_id=titular_id
                                        ))

        return render_template('usuarios_cogestores/usuarios_titulares/actualizar.html',
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                           usuario_rol_gestor_id=usuario_rol_gestor_id, 
                           gestor_id=gestor_id, 
                           titular_id=titular_id,
                           usuario_titular_id=usuario_titular_id,
                           usuario_titular=usuario_titular_info
                           )
    except Exception as e:
        flash(f'Error al actualizar el usuario titular: {str(e)}', 'danger')
        return redirect(url_for('uc_usuarios_titulares.usuarios_titulares', 
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id, 
                                titular_id=titular_id, 
                                usuario_titular_id=usuario_titular_id
                                ))

def usuarios_titulares_eliminar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, usuario_titular_id):
    '''
    Vista para eliminar un usuario titular
    '''
    try:
        # Eliminar el usuario titular
        delete = db.usuarios_titulares.delete_one({
            '_id': ObjectId(usuario_titular_id)
        })
        if delete.deleted_count > 0:
            flash('Usuario titular eliminado exitosamente', 'success')
        else:
            flash('No se pudo eliminar el usuario titular', 'danger')

        return redirect(url_for('uc_usuarios_titulares.usuarios_titulares',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id,
                                usuario_titular_id=usuario_titular_id
                                ))

    except Exception as e:
        flash(f'Error al eliminar el usuario titular: {str(e)}', 'danger')
        return redirect(url_for('uc_usuarios_titulares.usuarios_titulares', 
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id, 
                                titular_id=titular_id, 
                                usuario_titular_id=usuario_titular_id
                                ))


