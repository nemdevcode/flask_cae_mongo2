from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from utils.usuario_utils import verificar_usuario_existente, crear_usuario
from utils.rol_utils import obtener_rol, crear_rol, obtener_usuario_rol
from utils.usuario_rol_utils import crear_usuario_rol
from utils.token_utils import generar_token_verificacion
from utils.email_utils import enviar_email
from config import conexion_mongo

db = conexion_mongo()

def usuarios_contratas_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id):
    '''
    Función para mostrar la vista de usuarios de contratas
    '''
    try:
        # Obtener nombre de la contratas
        nombre_contrata = db.contratas.find_one({'_id': ObjectId(contrata_id)})['nombre_contrata']
        # Obtener parámetros de filtrado
        filtrar_usuario_contrata = request.form.get('filtrar_usuario_contrata', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
           return redirect(url_for('uc_usuarios_contratas.usuarios_contratas', 
                                    usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                    usuario_rol_gestor_id=usuario_rol_gestor_id,
                                    gestor_id=gestor_id,
                                    titular_id=titular_id,
                                    contrata_id=contrata_id
                                    ))
        
        # Construir la consulta base - buscar usuarios contratas donde el contrata_id sea el del contratas actual
        query = {'contrata_id': ObjectId(contrata_id)}

        # Aplicar filtros si existen
        if filtrar_usuario_contrata:
            # Obtener los usuarios que coinciden con el filtro
            usuarios_filtrados = list(db.usuarios.find({
                '$or': [
                    {'email': {'$regex': filtrar_usuario_contrata, '$options': 'i'}},
                    {'nombre_usuario': {'$regex': filtrar_usuario_contrata, '$options': 'i'}}
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
                {'alias_usuario_contrata': {'$regex': filtrar_usuario_contrata, '$options': 'i'}},
                {'usuario_rol_contrata_id': {'$in': rol_ids}}
            ]

        if filtrar_estado != 'todos':
            query['estado_usuario_contrata'] = filtrar_estado

        # Obtener los usuarios contratas asociados al contratas_id
        usuarios_contratas = []
        usuarios_contratas_cursor = db.usuarios_contratas.find(query)

        for uc in usuarios_contratas_cursor:
            # Obtener el usuario_rol del contratas usando la función obtener_usuario_rol
            usuario_rol_contrata = db.usuarios_roles.find_one({'_id': uc['usuario_rol_contrata_id']})

            if usuario_rol_contrata:
                # Obtener la información del usuario contratas
                usuario_contrata = db.usuarios.find_one({'_id': ObjectId(usuario_rol_contrata['usuario_id'])})

                if usuario_contrata:
                    contratas_info = {
                        '_id': uc['_id'],
                        'contrata_info': {
                            'alias': uc['alias_usuario_contrata'],
                            'estado_usuario_contrata': uc['estado_usuario_contrata']
                        },
                        'email': usuario_contrata['email'],
                        'nombre_usuario': usuario_contrata.get('nombre_usuario', '')
                    }
                    usuarios_contratas.append(contratas_info)

        return render_template('usuarios_cogestores/usuarios_contratas/listar.html',
                            usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                            usuario_rol_gestor_id=usuario_rol_gestor_id,
                            gestor_id=gestor_id,
                            titular_id=titular_id,
                            contrata_id=contrata_id,
                            usuarios_contratas=usuarios_contratas,
                            nombre_contrata=nombre_contrata,
                            filtrar_usuario_contrata=filtrar_usuario_contrata,
                            filtrar_estado=filtrar_estado
                            )
    except Exception as e:
        flash(f'Error al listar los usuarios de contratas: {str(e)}', 'danger')
        return redirect(url_for('uc_contratas.contratas_contrata', 
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id,
                                contrata_id=contrata_id
                                ))

def crear_usuario_contrata(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id, datos_formulario):
    '''
    Función para crear un usuario de contratas
    '''
    try:
        # Obtener los datos del formulario
        email = datos_formulario.get('email', '').strip().lower()
        alias = datos_formulario.get('alias', '').strip().upper()

        # Verificar si el usuario existe
        existe_usuario, usuario_contrata_id = verificar_usuario_existente(email)

        if existe_usuario:
            # Obtener rol de contratas
            existe_rol, rol_contrata_id = obtener_rol('contrata')

            if not existe_rol:
                rol_contrata_id = crear_rol('contrata')

            # Verificar si el usuario ya tiene el rol de contratas
            tiene_rol_contrata, usuario_rol_contrata_id = obtener_usuario_rol(usuario_contrata_id, rol_contrata_id)

            if tiene_rol_contrata:
                # Verificar si ya es usuario contratas para esta contratas específica
                usuario_contrata_existente = db.usuarios_contratas.find_one({
                    'usuario_rol_contrata_id': usuario_rol_contrata_id,
                    'contrata_id': ObjectId(contrata_id)
                })

                if usuario_contrata_existente:
                    flash('Este email ya está registrado como usuario de contrata para esta contrata', 'danger')
                    return False, {
                        'email': email,
                        'alias': alias
                    }
                
            else:
                # Si no tiene el rol de contrata, crearlo
                usuario_rol_contrata_id = crear_usuario_rol(usuario_contrata_id, rol_contrata_id)

            # Verificar si el usuario ya tiene el rol de contratas
            tiene_rol_contrata, usuario_rol_contrata_id = obtener_usuario_rol(usuario_contrata_id, rol_contrata_id)

            if tiene_rol_contrata:
                # Insertar el usuario contratas en la base de datos
                insert = db.usuarios_contratas.insert_one({
                    'usuario_rol_contrata_id': ObjectId(usuario_rol_contrata_id),
                    'contrata_id': ObjectId(contrata_id),
                    'alias_usuario_contrata': alias,
                    'estado_usuario_contrata': 'activo'
                })
                flash('Este email ya está registrado se ha creado un usuario para esta contrata', 'info')
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

        # Obtener rol de contratas y crear usuario_rol
        existe_rol, rol_contrata_id = obtener_rol('contrata')
        if not existe_rol:
            rol_contrata_id = crear_rol('contrata')

        usuario_rol_contrata_id = crear_usuario_rol(nuevo_usuario_id, rol_contrata_id)

        # Insertar el usuario contratas en la base de datos
        insert = db.usuarios_contratas.insert_one({
            'usuario_rol_contrata_id': ObjectId(usuario_rol_contrata_id),
            'contrata_id': ObjectId(contrata_id),
            'alias_usuario_contrata': alias,
            'estado_usuario_contrata': 'activo'
        })

        # Enviar email de verificación solo para usuarios nuevos
        link_verificacion = url_for('verificar_email', 
                                    token=token, 
                                    email=email, 
                                    _external=True
                                    )
        cuerpo_email = render_template('emails/registro_contrata.html',
                                        alias=alias,
                                        link_verificacion=link_verificacion
                                        )
        
        if enviar_email(email, "Activación de cuenta - CAE Accesible", cuerpo_email):
            if insert.inserted_id:
                flash('Usuario de contrata creada correctamente. Se ha enviado un email de activación.', 'success')
                return True, None
            else:
                flash('Error al crear el usuario de contrata', 'danger')
                return False, datos_formulario
        else:
            flash('Usuario de contrata creado pero hubo un error al enviar el email de activación.', 'warning')
            return False, datos_formulario
        
    except Exception as e:
        flash(f'Error al crear el usuario de contrata: {str(e)}', 'danger')
        return False, datos_formulario

def usuarios_contratas_crear_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id):
    '''
    Vista para crear un usuario de contrata
    '''
    try:
        if request.method == 'GET':
            datos_formulario = {}
            return render_template('usuarios_cogestores/usuarios_contratas/crear.html',
                                    usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                                    usuario_rol_gestor_id=usuario_rol_gestor_id, 
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id, 
                                    contrata_id=contrata_id, 
                                    datos_formulario=datos_formulario
                                    )
        
        if request.method == 'POST':
            # Crear usuario contratas
            creado, datos_formulario = crear_usuario_contrata(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id, request.form)
            if creado:
                return redirect(url_for('uc_usuarios_contratas.usuarios_contratas', 
                                        usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                        usuario_rol_gestor_id=usuario_rol_gestor_id,
                                        gestor_id=gestor_id, 
                                        titular_id=titular_id, 
                                        contrata_id=contrata_id
                                        ))
            
            else:
                return render_template('usuarios_cogestores/usuarios_contratas/crear.html',
                                        usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                        usuario_rol_gestor_id=usuario_rol_gestor_id,
                                        gestor_id=gestor_id, 
                                        titular_id=titular_id, 
                                        contrata_id=contrata_id, 
                                        datos_formulario=datos_formulario)
            
    except Exception as e:
        flash(f'Error al crear el usuario de contratas: {str(e)}', 'danger')
        return redirect(url_for('uc_usuarios_contratas.usuarios_contratas', 
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id, 
                                titular_id=titular_id, 
                                contrata_id=contrata_id
                                ))

def actualizar_usuario_contrata(usuario_contrata_id, datos_formulario):
    '''
    Función para actualizar un usuario contratas
    '''
    try:
        # Obtener los datos del formulario
        alias = datos_formulario.get('alias', '').strip().upper()
        estado_usuario_contrata = datos_formulario.get('estado_usuario_contrata', 'activo')

        # Actualizar el usuario contratas
        actualizar = db.usuarios_contratas.update_one(
            {'_id': ObjectId(usuario_contrata_id)},
            {'$set': {
                'alias_usuario_contrata': alias,
                'estado_usuario_contrata': estado_usuario_contrata
            }}
        )

        if actualizar.modified_count > 0:
            flash('Usuario de contrata actualizado correctamente', 'success')
            return True, None
        else:
            flash('No se realizaron cambios en el usuario de contrata', 'info')
            return True, None

    except Exception as e:
        flash(f'Error al actualizar el usuario de contrata: {str(e)}', 'danger')
        return False, datos_formulario

def usuarios_contratas_actualizar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id, usuario_contrata_id):
    '''
    Vista para actualizar un usuario contratas
    '''
    try:
        # Obtener el usuario contratas a actualizar
        usuario_contrata = db.usuarios_contratas.find_one({'_id': ObjectId(usuario_contrata_id)})

        # Obtener el usuario_rol del contratas
        usuario_rol_contrata = db.usuarios_roles.find_one({'_id': usuario_contrata['usuario_rol_contrata_id']})

        # Obtener la información del usuario
        usuario = db.usuarios.find_one({'_id': ObjectId(usuario_rol_contrata['usuario_id'])})

        # Obtener la información del usuario contratas
        usuario_contrata_info = {
            '_id': usuario_contrata['_id'],
            'contrata_info': {
                'alias': usuario_contrata['alias_usuario_contrata'],
                'estado_usuario_contrata': usuario_contrata['estado_usuario_contrata']
            },
            'email': usuario['email'],
            'nombre_usuario': usuario.get('nombre_usuario', '')
        }

         # Si es una petición POST, procesar el formulario
        if request.method == 'POST':
            actualizar = actualizar_usuario_contrata(usuario_contrata_id, request.form)
            if actualizar:
                return redirect(url_for('uc_usuarios_contratas.usuarios_contratas', 
                                        usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                        usuario_rol_gestor_id=usuario_rol_gestor_id,
                                        gestor_id=gestor_id, 
                                        titular_id=titular_id,
                                        contrata_id=contrata_id
                                        ))
            
        return render_template('usuarios_cogestores/usuarios_contratas/actualizar.html', 
                               usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                               usuario_rol_gestor_id=usuario_rol_gestor_id, 
                               gestor_id=gestor_id, 
                               titular_id=titular_id, 
                               contrata_id=contrata_id, 
                               usuario_contrata_id=usuario_contrata_id, 
                               usuario_contrata=usuario_contrata_info
                               )
    
    except Exception as e:
        flash(f'Error al actualizar el usuario de contratas: {str(e)}', 'danger')
        return redirect(url_for('uc_usuarios_contratas.usuarios_contratas', 
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id, 
                                titular_id=titular_id,
                                contrata_id=contrata_id
                                ))

def usuarios_contratas_eliminar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id, usuario_contrata_id):
    '''
    Vista para eliminar un usuario contratas
    '''
    try:
        # Eliminar el usuario contratas
        delete = db.usuarios_contratas.delete_one({'_id': ObjectId(usuario_contrata_id)})

        if delete.deleted_count > 0:
            flash('Usuario de contrata eliminado correctamente', 'success')
        else:
            flash('No se pudo eliminar el usuario de contrata', 'danger')

        return redirect(url_for('uc_usuarios_contratas.usuarios_contratas', 
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id,
                                contrata_id=contrata_id
                                ))
    except Exception as e:
        flash(f'Error al eliminar el usuario de contratas: {str(e)}', 'danger')
        return redirect(url_for('uc_usuarios_contratas.usuarios_contratas', 
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id,
                                contrata_id=contrata_id
                                ))


