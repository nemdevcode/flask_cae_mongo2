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
from utils.usuario_contrata_utils import crear_usuario_contrata
from utils.contrata_utils import obtener_contrata_por_id
from utils.token_utils import generar_token_verificacion
from utils.email_utils import enviar_email
from config import conexion_mongo

db = conexion_mongo()

def verificaciones_consultas(gestor_id, titular_id, contrata_id):
    '''
    Función auxiliar para verificar permisos de gestor y obtener información necesaria
    Retorna:
        - (False, respuesta_redireccion) si hay algún error
        - (True, (usuario, usuario_rol_id, gestor, titular, contrata)) si todo está correcto
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
        return False, redirect(url_for('usuarios_gestores.usuarios_gestores_gestor', 
                                       gestor_id=gestor_id
                                       ))

    # Obtener la información del titular
    titular = obtener_titular_por_id(titular_id)
    if not titular:
        flash('Titular no encontrado', 'danger')
        return False, redirect(url_for('ug_titulares.titulares_titular', 
                                       gestor_id=gestor_id, 
                                       titular_id=titular_id
                                       ))
    
    # Obtener la información de la contrata
    contrata = obtener_contrata_por_id(contrata_id)
    if not contrata:
        flash('Contrata no encontrada', 'danger')
        return False, redirect(url_for('ug_contratas.contratas_contrata', 
                                       gestor_id=gestor_id, 
                                       titular_id=titular_id, 
                                       contrata_id=contrata_id
                                       ))

    return True, (usuario, usuario_rol_id, gestor, titular, contrata)

def usuarios_contratas_vista(gestor_id, titular_id, contrata_id):
    '''
    Vista para listar los usuarios contratatas de la contratata seleccionada
    '''
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id, contrata_id)
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_id, gestor, titular, contrata = resultado
        nombre_gestor = gestor.get('nombre_gestor', 'Gestor')

        # Obtener parámetros de filtrado
        filtrar_contrata = request.form.get('filtrar_contrata', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('ug_usuarios_contratas.usuarios_contratas', 
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id, 
                                    contrata_id=contrata_id
                                    ))
        
        # Construir la consulta base - buscar usuarios contratas donde el contrata_id sea el de la contratata actual
        query = {'contrata_id': ObjectId(contrata_id)}
        
        # Aplicar filtros si existen
        if filtrar_contrata:
            query['alias_usuario_contrata'] = {'$regex': filtrar_contrata, '$options': 'i'}

        if filtrar_estado != 'todos':
            query['estado_usuario_contrata'] = filtrar_estado
        

        # Obtener los usuarios contratas asociados al titular_id
        usuarios_contratas = []
        usuarios_contratas_cursor = db.usuarios_contratas.find(query)
        
        # Obtener el rol de titular
        existe_rol, rol_titular_id = obtener_rol('titular')
        if not existe_rol:
            flash('Rol de titular no encontrado', 'danger')
            return redirect(url_for('ug_titulares.titulares_titular', 
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id
                                    ))
        
        # Diccionario para almacenar las IDs de los usuarios contratas
        usuario_contrata_ids = {}
        
        for uc in usuarios_contratas_cursor:
            # Obtener el usuario_rol del titular usando la función obtener_usuario_rol
            usuario_rol = db.usuarios_roles.find_one({'_id': uc['usuario_rol_contrata_id']})
            
            if usuario_rol:
                # Obtener la información del usuario titular
                usuario_contrata = db.usuarios.find_one({'_id': ObjectId(usuario_rol['usuario_id'])})
                
                if usuario_contrata:
                    # Guardar el ID del usuario contrata en el diccionario
                    uc_id_str = str(uc['_id'])
                    usuario_contrata_ids[uc_id_str] = uc_id_str
                    
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

        return render_template('usuarios_gestores/usuarios_contratas/listar.html',
                               gestor_id=gestor_id,
                               titular_id=titular_id,
                               contrata_id=contrata_id,
                               usuario_contrata_ids=usuario_contrata_ids,
                               nombre_gestor=nombre_gestor,
                               titular=titular,
                               contrata=contrata,
                               usuarios_contratas=usuarios_contratas,
                               filtrar_estado=filtrar_estado
                               )

    except Exception as e:
        flash(f'Error al listar los usuarios contratas: {str(e)}', 'danger')
        return redirect(url_for('ug_contratas.contratas_contrata', 
                                gestor_id=gestor_id, 
                                titular_id=titular_id, 
                                contrata_id=contrata_id
                                ))

def usuarios_contratas_crear_vista(gestor_id, titular_id, contrata_id):
    '''
    Vista para crear un nuevo usuario contrata de la contratata seleccionada
    '''
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id, contrata_id)
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_id, gestor, titular, contrata = resultado
        nombre_gestor = gestor.get('nombre_gestor', 'Gestor')

        if request.method == 'GET':
            return render_template('usuarios_gestores/usuarios_contratas/crear.html',
                                    gestor_id=gestor_id,
                                    nombre_gestor=nombre_gestor,
                                    titular=titular,
                                    contrata=contrata
                                    )
        
        if request.method == 'POST':
            # Obtener datos del formulario
            email = request.form.get('email', '').strip().lower()
            alias = request.form.get('alias', '').strip().upper()

            # Verificar si el usuario existe
            existe_usuario, usuario_contrata_id = verificar_usuario_existente(email)

            if existe_usuario:
                # Obtener rol de contrata
                existe_rol, rol_contrata_id = obtener_rol('contrata')
                
                if not existe_rol:
                    rol_contrata_id = crear_rol('contrata')
                
                # Verificar si el usuario ya tiene el rol de contrata
                tiene_rol_contrata, usuario_rol_contrata_id = obtener_usuario_rol(usuario_contrata_id, rol_contrata_id)

                if tiene_rol_contrata:
                    # Verificar si ya es usuario titular para esta contrata específica
                    contrata_existente = db.usuarios_contratas.find_one({
                        'usuario_rol_contrata_id': usuario_rol_contrata_id,
                        'contrata_id': ObjectId(contrata_id)
                    })
                    
                    if contrata_existente:
                        flash('Este email ya está registrado como usuario-contrata para esta contrata', 'danger')
                        return render_template('usuarios_gestores/usuarios_contratas/crear.html',
                                                gestor_id=gestor_id,
                                                datos_formulario=request.form,
                                                nombre_gestor=nombre_gestor,
                                                titular=titular,
                                                contrata=contrata
                                                )
                else:
                    # Si no tiene el rol de contrata, crearlo
                    usuario_rol_contrata_id = crear_usuario_rol(usuario_contrata_id, rol_contrata_id)
                
                # Crear el usuario contrata
                crear_usuario_contrata(usuario_rol_contrata_id, contrata_id, alias)
                flash('Este email ya está registrado, será asignado como usuario-contrata para esta contrata', 'success')
                return redirect(url_for('ug_usuarios_contratas.usuarios_contratas', 
                                        gestor_id=gestor_id, 
                                        titular_id=titular_id, 
                                        contrata_id=contrata_id
                                        ))

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
            
            # Obtener rol de contrata y crear usuario_rol
            existe_rol, rol_contrata_id = obtener_rol('contrata')
            if not existe_rol:
                rol_contrata_id = crear_rol('contrata')
            
            usuario_rol_contrata_id = crear_usuario_rol(nuevo_usuario_id, rol_contrata_id)
            
            # Crear el usuario contrata
            crear_usuario_contrata(usuario_rol_contrata_id, contrata_id, alias)

            # Enviar email de verificación solo para usuarios nuevos
            link_verificacion = url_for('verificar_email', 
                                        token=token, 
                                        email=email, _external=True
                                        )
            cuerpo_email = render_template('emails/registro_contrata.html',
                                           alias=alias,
                                           link_verificacion=link_verificacion,
                                           contrata=contrata
                                           )

            if enviar_email(email, "Activación de cuenta - CAE Accesible", cuerpo_email):
                flash('Usuario contrata creado correctamente. Se ha enviado un email de activación.', 'success')
            else:
                flash('Usuario contrata creado pero hubo un error al enviar el email de activación.', 'warning')

            return redirect(url_for('ug_usuarios_contratas.usuarios_contratas', 
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id, 
                                    contrata_id=contrata_id
                                    ))

    except Exception as e:
        flash(f'Error al crear el usuario contrata: {str(e)}', 'danger')
        return render_template('usuarios_gestores/usuarios_contratas/crear.html',
                               gestor_id=gestor_id,
                               nombre_gestor=nombre_gestor,
                               titular=titular,
                               contrata=contrata,
                               datos_formulario=request.form
                               )

def usuarios_contratas_actualizar_vista(gestor_id, titular_id, contrata_id, usuario_contrata_id):
    '''
    Vista para actualizar un usuario contrata de la contrata seleccionada
    '''
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id, contrata_id)
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_id, gestor, titular, contrata   = resultado
        nombre_gestor = gestor.get('nombre_gestor', 'Gestor')

        # Obtener el usuario contrata a actualizar
        usuario_contrata = db.usuarios_contratas.find_one({'_id': ObjectId(usuario_contrata_id)})
        if not usuario_contrata:
            flash('Usuario contrata no encontrado', 'danger')
            return redirect(url_for('ug_usuarios_contratas.usuarios_contratas', 
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id, 
                                    contrata_id=contrata_id
                                    ))

        # Obtener el usuario_rol del titular
        usuario_rol = db.usuarios_roles.find_one({'_id': usuario_contrata['usuario_rol_contrata_id']})
        if not usuario_rol:
            flash('Usuario rol no encontrado', 'danger')
            return redirect(url_for('ug_usuarios_contratas.usuarios_contratas', 
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id, 
                                    contrata_id=contrata_id
                                    ))

        # Obtener la información del usuario contrata
        usuario = db.usuarios.find_one({'_id': ObjectId(usuario_rol['usuario_id'])})
        if not usuario:
            flash('Usuario no encontrado', 'danger')
            return redirect(url_for('ug_usuarios_contratas.usuarios_contratas', 
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id, 
                                    contrata_id=contrata_id
                                    ))

        # Preparar la información del usuario contrata en el formato que espera el template
        usuario_contrata_info = {
            '_id': usuario_contrata['_id'],
            'contrata_info': {
                'alias': usuario_contrata['alias_usuario_contrata'],
                'estado_usuario_contrata': usuario_contrata['estado_usuario_contrata']
            },
            'email': usuario['email']
        }

        if request.method == 'GET':
            return render_template('usuarios_gestores/usuarios_contratas/actualizar.html',
                                   gestor_id=gestor_id,
                                   titular_id=titular_id,
                                   contrata_id=contrata_id,
                                   usuario_contrata_id=usuario_contrata_id,
                                   titular=titular,
                                   usuario_contrata=usuario_contrata_info
                                   )

        if request.method == 'POST':
            # Obtener datos del formulario
            alias = request.form.get('alias', '').strip().upper()
            estado_usuario_contrata = request.form.get('estado_usuario_contrata', 'activo')

            # Actualizar el usuario titular
            db.usuarios_contratas.update_one(
                {'_id': ObjectId(usuario_contrata_id)},
                {
                    '$set': {
                        'alias_usuario_contrata': alias,
                        'estado_usuario_contrata': estado_usuario_contrata
                    }
                }
            )

            flash('Usuario de contrata actualizado correctamente', 'success')
            return redirect(url_for('ug_usuarios_contratas.usuarios_contratas', 
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id, 
                                    contrata_id=contrata_id
                                    ))

    except Exception as e:
        flash(f'Error al actualizar el usuario contrata: {str(e)}', 'danger')
        return redirect(url_for('ug_usuarios_contratas.usuarios_contratas', 
                                gestor_id=gestor_id, 
                                titular_id=titular_id, 
                                contrata_id=contrata_id
                                ))

def usuarios_contratas_eliminar_vista(gestor_id, titular_id, contrata_id, usuario_contrata_id):
    '''
    Vista para eliminar un usuario contratata de la contrata seleccionada
    '''
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id, contrata_id)
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_id, gestor, titular, contrata = resultado

        # Obtener el usuario contrata a eliminar
        usuario_contrata = db.usuarios_contratas.find_one({'_id': ObjectId(usuario_contrata_id)})
        if not usuario_contrata:
            flash('Usuario contratata no encontrado', 'danger')
            return redirect(url_for('ug_usuarios_contratas.usuarios_contratas', 
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id, 
                                    contrata_id=contrata_id
                                    ))

        # Eliminar el usuario contratata
        result = db.usuarios_contratas.delete_one({'_id': ObjectId(usuario_contrata_id)})

        if result.deleted_count > 0:
            flash('Usuario contratata eliminado exitosamente', 'success')
            return redirect(url_for('ug_usuarios_contratas.usuarios_contratas', 
                                 gestor_id=gestor_id, 
                                 titular_id=titular_id, 
                                 contrata_id=contrata_id
                                 ))
        else:
            flash('No se pudo eliminar el usuario contratata', 'danger')
            return redirect(url_for('ug_usuarios_contratas.usuarios_contratas', 
                                 gestor_id=gestor_id, 
                                 titular_id=titular_id, 
                                 contrata_id=contrata_id
                                 ))

    except Exception as e:
        flash(f'Error al eliminar el usuario contratata: {str(e)}', 'danger')
        return redirect(url_for('ug_usuarios_contratas.usuarios_contratas', 
                                gestor_id=gestor_id, 
                                titular_id=titular_id, 
                                contrata_id=contrata_id
                                ))

