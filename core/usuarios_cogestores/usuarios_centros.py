from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from utils.usuario_utils import verificar_usuario_existente, crear_usuario
from utils.rol_utils import obtener_rol, crear_rol, obtener_usuario_rol
from utils.usuario_rol_utils import crear_usuario_rol
from utils.token_utils import generar_token_verificacion
from utils.email_utils import enviar_email
from config import conexion_mongo

db = conexion_mongo()

def usuarios_centros_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id):
    '''
    Función para mostrar la vista de usuarios de centros
    '''
    try:
        # Obtener nombre del centro
        nombre_centro = db.centros.find_one({'_id': ObjectId(centro_id)})['nombre_centro']
        # Obtener parámetros de filtrado
        filtrar_usuario_centro = request.form.get('filtrar_usuario_centro', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
           return redirect(url_for('uc_usuarios_centros.usuarios_centros', 
                                    usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                    usuario_rol_gestor_id=usuario_rol_gestor_id,
                                    gestor_id=gestor_id,
                                    titular_id=titular_id,
                                    centro_id=centro_id
                                    ))
        
        # Construir la consulta base - buscar usuarios centros donde el centro_id sea el del centro actual
        query = {'centro_id': ObjectId(centro_id)}

        # Aplicar filtros si existen
        if filtrar_usuario_centro:
            # Obtener los usuarios que coinciden con el filtro
            usuarios_filtrados = list(db.usuarios.find({
                '$or': [
                    {'email': {'$regex': filtrar_usuario_centro, '$options': 'i'}},
                    {'nombre_usuario': {'$regex': filtrar_usuario_centro, '$options': 'i'}}
                ]
            }))
            
            # Obtener los IDs de los usuarios filtrados
            usuario_ids = [ObjectId(u['_id']) for u in usuarios_filtrados]
            
            # Obtener los roles de usuario que corresponden a estos usuarios
            roles_filtrados = list(db.usuarios_roles.find({
                'usuario_id': {'$in': usuario_ids}
            }))
            
            # Obtener los IDs de los roles filtrados
            rol_ids = [ObjectId(r['_id']) for r in roles_filtrados]
            
            # Agregar el filtro de alias y los IDs de roles a la consulta
            query['$or'] = [
                {'alias_usuario_centro': {'$regex': filtrar_usuario_centro, '$options': 'i'}},
                {'usuario_rol_centro_id': {'$in': rol_ids}}
            ]

        if filtrar_estado != 'todos':
            query['estado_usuario_centro'] = filtrar_estado

        # Obtener los usuarios centros asociados al centro_id
        usuarios_centros = []
        usuarios_centros_cursor = db.usuarios_centros.find(query)

        for uc in usuarios_centros_cursor:
            # Obtener el usuario_rol del centro usando la función obtener_usuario_rol
            usuario_rol_centro = db.usuarios_roles.find_one({'_id': uc['usuario_rol_centro_id']})

            if usuario_rol_centro:
                # Obtener la información del usuario centro
                usuario_centro = db.usuarios.find_one({'_id': ObjectId(usuario_rol_centro['usuario_id'])})

                if usuario_centro:
                    centro_info = {
                        '_id': uc['_id'],
                        'centro_info': {
                            'alias': uc['alias_usuario_centro'],
                            'estado_usuario_centro': uc['estado_usuario_centro']
                        },
                        'email': usuario_centro['email'],
                        'nombre_usuario': usuario_centro.get('nombre_usuario', '')
                    }
                    usuarios_centros.append(centro_info)

        return render_template('usuarios_cogestores/usuarios_centros/listar.html',
                            usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                            usuario_rol_gestor_id=usuario_rol_gestor_id,
                            gestor_id=gestor_id,
                            titular_id=titular_id,
                            centro_id=centro_id,
                            usuarios_centros=usuarios_centros,
                            nombre_centro=nombre_centro,
                            filtrar_usuario_centro=filtrar_usuario_centro,
                            filtrar_estado=filtrar_estado
                            )
    except Exception as e:
        flash(f'Error al listar los usuarios de centros: {str(e)}', 'danger')
        return redirect(url_for('uc_centros.centros_centro', 
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id,
                                centro_id=centro_id
                                ))

def crear_usuario_centro(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id, datos_formulario):
    '''
    Función para crear un usuario centro
    '''
    try:
        # Obtener los datos del formulario
        email = datos_formulario.get('email', '').strip().lower()
        alias = datos_formulario.get('alias', '').strip().upper()

        # Verificar si el usuario existe
        existe_usuario, usuario_centro_id = verificar_usuario_existente(email)

        if existe_usuario:
            # Obtener rol de centro
            existe_rol, rol_centro_id = obtener_rol('centro')

            if not existe_rol:
                rol_centro_id = crear_rol('centro')

            # Verificar si el usuario ya tiene el rol de centro
            tiene_rol_centro, usuario_rol_centro_id = obtener_usuario_rol(usuario_centro_id, rol_centro_id)

            if tiene_rol_centro:
                # Verificar si ya es usuario centro para este centro específico
                usuario_centro_existente = db.usuarios_centros.find_one({
                    'usuario_rol_centro_id': usuario_rol_centro_id,
                    'centro_id': ObjectId(centro_id)
                })

                if usuario_centro_existente:
                    flash('Este email ya está registrado como usuario centro para este centro', 'danger')
                    return False, {
                        'email': email,
                        'alias': alias
                    }
                
            else:
                # Si no tiene el rol de centro, crearlo
                usuario_rol_centro_id = crear_usuario_rol(usuario_centro_id, rol_centro_id)

            # # Obtener rol de centro
            # existe_rol, rol_centro_id = obtener_rol('centro')

            # if not existe_rol:
            #     rol_centro_id = crear_rol('centro')

            # Verificar si el usuario ya tiene el rol de centro
            tiene_rol_centro, usuario_rol_centro_id = obtener_usuario_rol(usuario_centro_id, rol_centro_id)

            if tiene_rol_centro:
                # Insertar el usuario centro en la base de datos
                insert = db.usuarios_centros.insert_one({
                    'usuario_rol_centro_id': ObjectId(usuario_rol_centro_id),
                    'centro_id': ObjectId(centro_id),
                    'alias_usuario_centro': alias,
                    'estado_usuario_centro': 'activo'
                })
                flash('Este email ya está registrado se ha creado un usuario para este centro', 'info')
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

        # Obtener rol de centro y crear usuario_rol
        existe_rol, rol_centro_id = obtener_rol('centro')
        if not existe_rol:
            rol_centro_id = crear_rol('centro')

        usuario_rol_centro_id = crear_usuario_rol(nuevo_usuario_id, rol_centro_id)

        # Insertar el usuario centro en la base de datos
        insert = db.usuarios_centros.insert_one({
            'usuario_rol_centro_id': ObjectId(usuario_rol_centro_id),
            'centro_id': ObjectId(centro_id),
            'alias_usuario_centro': alias,
            'estado_usuario_centro': 'activo'
        })

        # Enviar email de verificación solo para usuarios nuevos
        link_verificacion = url_for('verificar_email', 
                                    token=token, 
                                    email=email, 
                                    _external=True
                                    )
        cuerpo_email = render_template('emails/registro_centro.html',
                                        alias=alias,
                                        link_verificacion=link_verificacion
                                        )
        
        if enviar_email(email, "Activación de cuenta - CAE Accesible", cuerpo_email):
            if insert.inserted_id:
                flash('Usuario centro creado correctamente. Se ha enviado un email de activación.', 'success')
                return True, None
            else:
                flash('Error al crear el usuario centro', 'danger')
                return False, datos_formulario
        else:
            flash('Usuario centro creado pero hubo un error al enviar el email de activación.', 'warning')
            return False, datos_formulario
        
    except Exception as e:
        flash(f'Error al crear el usuario de centro: {str(e)}', 'danger')
        return False, datos_formulario

def usuarios_centros_crear_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id):
    '''
    Vista para crear un usuario centro
    '''
    try:
        if request.method == 'GET':
            datos_formulario = {}
            return render_template('usuarios_cogestores/usuarios_centros/crear.html',
                                    usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                                    usuario_rol_gestor_id=usuario_rol_gestor_id, 
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id, 
                                    centro_id=centro_id, 
                                    datos_formulario=datos_formulario
                                    )
        
        if request.method == 'POST':
            # Crear usuario centro
            creado, datos_formulario = crear_usuario_centro(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id, request.form)
            if creado:
                return redirect(url_for('uc_usuarios_centros.usuarios_centros', 
                                        usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                        usuario_rol_gestor_id=usuario_rol_gestor_id,
                                        gestor_id=gestor_id, 
                                        titular_id=titular_id, 
                                        centro_id=centro_id
                                        ))
            
            else:
                return render_template('usuarios_cogestores/usuarios_centros/crear.html',
                                        usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                        usuario_rol_gestor_id=usuario_rol_gestor_id,
                                        gestor_id=gestor_id, 
                                        titular_id=titular_id, 
                                        centro_id=centro_id, 
                                        datos_formulario=datos_formulario)
            
    except Exception as e:
        flash(f'Error al crear el usuario de centro: {str(e)}', 'danger')
        return redirect(url_for('uc_usuarios_centros.usuarios_centros', 
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id, 
                                titular_id=titular_id, 
                                centro_id=centro_id
                                ))
    
def actualizar_usuario_centro(usuario_centro_id, datos_formulario):
    '''
    Función para actualizar un usuario centro
    '''
    try:
        # Obtener los datos del formulario
        alias = datos_formulario.get('alias', '').strip().upper()
        estado_usuario_centro = datos_formulario.get('estado_usuario_centro', 'activo')

        # Actualizar el usuario centro
        actualizar = db.usuarios_centros.update_one(
            {'_id': ObjectId(usuario_centro_id)},
            {'$set': {
                'alias_usuario_centro': alias,
                'estado_usuario_centro': estado_usuario_centro
            }}
        )

        if actualizar.modified_count > 0:
            flash('Usuario de centro actualizado correctamente', 'success')
            return True, None
        else:
            flash('No se realizaron cambios en el usuario de centro', 'info')
            return True, None

    except Exception as e:
        flash(f'Error al actualizar el usuario de centro: {str(e)}', 'danger')
        return False, datos_formulario

def usuarios_centros_actualizar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id, usuario_centro_id):
    '''
    Vista para actualizar un usuario centro
    '''
    try:
        # Obtener el usuario centro a actualizar
        usuario_centro = db.usuarios_centros.find_one({'_id': ObjectId(usuario_centro_id)})

        # Obtener el usuario_rol del centro
        usuario_rol_centro = db.usuarios_roles.find_one({'_id': usuario_centro['usuario_rol_centro_id']})

        # Obtener la información del usuario
        usuario = db.usuarios.find_one({'_id': ObjectId(usuario_rol_centro['usuario_id'])})

        # Obtener la información del usuario centro
        usuario_centro_info = {
            '_id': usuario_centro['_id'],
            'centro_info': {
                'alias': usuario_centro['alias_usuario_centro'],
                'estado_usuario_centro': usuario_centro['estado_usuario_centro']
            },
            'email': usuario['email'],
            'nombre_usuario': usuario.get('nombre_usuario', '')
        }

         # Si es una petición POST, procesar el formulario
        if request.method == 'POST':
            actualizar = actualizar_usuario_centro(usuario_centro_id, request.form)
            if actualizar:
                return redirect(url_for('uc_usuarios_centros.usuarios_centros', 
                                        usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                        usuario_rol_gestor_id=usuario_rol_gestor_id,
                                        gestor_id=gestor_id, 
                                        titular_id=titular_id,
                                        centro_id=centro_id
                                        ))
            
        return render_template('usuarios_cogestores/usuarios_centros/actualizar.html', 
                               usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                               usuario_rol_gestor_id=usuario_rol_gestor_id, 
                               gestor_id=gestor_id, 
                               titular_id=titular_id, 
                               centro_id=centro_id, 
                               usuario_centro_id=usuario_centro_id, 
                               usuario_centro=usuario_centro_info
                               )
    
    except Exception as e:
        flash(f'Error al actualizar el usuario de centro: {str(e)}', 'danger')
        return redirect(url_for('uc_usuarios_centros.usuarios_centros', 
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id, 
                                titular_id=titular_id,
                                centro_id=centro_id
                                ))

def usuarios_centros_eliminar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id, usuario_centro_id):
    '''
    Vista para eliminar un usuario centro
    '''
    try:
        # Eliminar el usuario centro
        delete = db.usuarios_centros.delete_one({'_id': ObjectId(usuario_centro_id)})

        if delete.deleted_count > 0:
            flash('Usuario de centro eliminado correctamente', 'success')
        else:
            flash('No se pudo eliminar el usuario de centro', 'danger')

        return redirect(url_for('uc_usuarios_centros.usuarios_centros', 
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id,
                                centro_id=centro_id
                                ))
    except Exception as e:
        flash(f'Error al eliminar el usuario de centro: {str(e)}', 'danger')
        return redirect(url_for('uc_usuarios_centros.usuarios_centros', 
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id,
                                centro_id=centro_id
                                ))
