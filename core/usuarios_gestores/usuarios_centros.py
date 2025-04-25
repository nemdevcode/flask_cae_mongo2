from flask import render_template, redirect, url_for, request, session, flash
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
from utils.gestor_utils import obtener_gestor_por_usuario
from utils.titular_utils import obtener_titular_por_id
from utils.usuario_centro_utils import crear_usuario_centro
from utils.centros_utils import obtener_centro_por_id
from utils.token_utils import generar_token_verificacion
from utils.email_utils import enviar_email
from utils.usuario_rol_utils import obtener_usuario_rol, crear_usuario_rol
from config import conexion_mongo

db = conexion_mongo()

def verificaciones_consultas(gestor_id, titular_id, centro_id):
    '''
    Función auxiliar para verificar permisos de gestor y obtener información necesaria
    Retorna:
        - (False, respuesta_redireccion) si hay algún error
        - (True, (usuario, usuario_rol_id, gestor, titular, centro)) si todo está correcto
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
    
    # Obtener la información del centro
    centro = obtener_centro_por_id(centro_id)
    if not centro:
        flash('Centro no encontrado', 'danger')
        return False, redirect(url_for('ug_centros.centros_centro', 
                                       gestor_id=gestor_id, 
                                       titular_id=titular_id, 
                                       centro_id=centro_id
                                       ))

    return True, (usuario, usuario_rol_id, gestor, titular, centro)

def usuarios_centros_vista(gestor_id, titular_id, centro_id):
    '''
    Vista para listar los usuarios centros de un centro seleccionado
    '''
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id, centro_id)
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_id, gestor, titular, centro = resultado
        nombre_gestor = gestor.get('nombre_gestor', 'Gestor')

        # Obtener parámetros de filtrado
        filtrar_centro = request.form.get('filtrar_centro', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('ug_usuarios_centros.usuarios_centros', 
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id, 
                                    centro_id=centro_id
                                    ))
        
        # Construir la consulta base - buscar usuarios centros donde el centro_id sea el del centro actual
        query = {'centro_id': ObjectId(centro_id)}
        
        # Aplicar filtros si existen
        if filtrar_centro:
            query['alias_usuario_centro'] = {'$regex': filtrar_centro, '$options': 'i'}

        if filtrar_estado != 'todos':
            query['estado_usuario_centro'] = filtrar_estado
        

        # Obtener los usuarios centros asociados al titular_id
        usuarios_centros = []
        usuarios_centros_cursor = db.usuarios_centros.find(query)
        
        # Obtener el rol de titular
        existe_rol, rol_titular_id = obtener_rol('titular')
        if not existe_rol:
            flash('Rol de titular no encontrado', 'danger')
            return redirect(url_for('ug_titulares.titulares_titular', 
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id
                                    ))
        
        # Diccionario para almacenar las IDs de los usuarios centros
        usuario_centro_ids = {}
        
        for uc in usuarios_centros_cursor:
            # Obtener el usuario_rol del titular usando la función obtener_usuario_rol
            usuario_rol = db.usuarios_roles.find_one({'_id': uc['usuario_rol_centro_id']})
            
            if usuario_rol:
                # Obtener la información del usuario titular
                usuario_centro = db.usuarios.find_one({'_id': ObjectId(usuario_rol['usuario_id'])})
                
                if usuario_centro:
                    # Guardar el ID del usuario centro en el diccionario
                    uc_id_str = str(uc['_id'])
                    usuario_centro_ids[uc_id_str] = uc_id_str
                    
                    centros_info = {
                        '_id': uc['_id'],
                        'centro_info': {
                            'alias': uc['alias_usuario_centro'],
                            'estado_usuario_centro': uc['estado_usuario_centro']
                        },
                        'email': usuario_centro['email'],
                        'nombre_usuario': usuario_centro.get('nombre_usuario', '')
                    }
                    usuarios_centros.append(centros_info)

        return render_template('usuarios_gestores/usuarios_centros/listar.html',
                               gestor_id=gestor_id,
                               titular_id=titular_id,
                               centro_id=centro_id,
                               usuario_centro_ids=usuario_centro_ids,
                               nombre_gestor=nombre_gestor,
                               titular=titular,
                               centro=centro,
                               usuarios_centros=usuarios_centros,
                               filtrar_estado=filtrar_estado
                               )

    except Exception as e:
        flash(f'Error al listar los usuarios centros: {str(e)}', 'danger')
        return redirect(url_for('ug_centros.centros_centro', 
                                gestor_id=gestor_id, 
                                titular_id=titular_id, 
                                centro_id=centro_id
                                ))

def usuarios_centros_crear_vista(gestor_id, titular_id, centro_id):
    '''
    Vista para crear un nuevo usuario centro de un centro seleccionado
    '''
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id, centro_id)
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_id, gestor, titular, centro = resultado
        nombre_gestor = gestor.get('nombre_gestor', 'Gestor')

        if request.method == 'GET':
            return render_template('usuarios_gestores/usuarios_centros/crear.html',
                                    gestor_id=gestor_id,
                                    nombre_gestor=nombre_gestor,
                                    titular=titular,
                                    centro=centro
                                    )
        
        if request.method == 'POST':
            # Obtener datos del formulario
            email = request.form.get('email', '').strip().lower()
            alias = request.form.get('alias', '').strip().upper()

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
                    centro_existente = db.usuarios_centros.find_one({
                        'usuario_rol_centro_id': usuario_rol_centro_id,
                        'centro_id': ObjectId(centro_id)
                    })
                    
                    if centro_existente:
                        flash('Este email ya está registrado como usuario-centro para este centro', 'danger')
                        return render_template('usuarios_gestores/usuarios_centros/crear.html',
                                                gestor_id=gestor_id,
                                                nombre_gestor=nombre_gestor,
                                                titular=titular,
                                                centro=centro,
                                                datos_formulario=request.form
                                                )
                else:
                    # Si no tiene el rol de centro, crearlo
                    usuario_rol_centro_id = crear_usuario_rol(usuario_centro_id, rol_centro_id)
                
                # Crear el usuario centro
                crear_usuario_centro(usuario_rol_centro_id, centro_id, alias)
                flash('Este email ya está registrado, será asignado como usuario-centro para este centro', 'success')
                return redirect(url_for('ug_usuarios_centros.usuarios_centros', 
                                        gestor_id=gestor_id, 
                                        titular_id=titular_id, 
                                        centro_id=centro_id
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
            
            # Obtener rol de centro y crear usuario_rol
            existe_rol, rol_centro_id = obtener_rol('centro')
            if not existe_rol:
                rol_centro_id = crear_rol('centro')
            
            usuario_rol_centro_id = crear_usuario_rol(nuevo_usuario_id, rol_centro_id)
            
            # Crear el usuario centro
            crear_usuario_centro(usuario_rol_centro_id, centro_id, alias)

            # Enviar email de verificación solo para usuarios nuevos
            link_verificacion = url_for('verificar_email', 
                                        token=token, 
                                        email=email, _external=True
                                        )
            cuerpo_email = render_template('emails/registro_centro.html',
                                           alias=alias,
                                           link_verificacion=link_verificacion,
                                           centro=centro
                                           )

            if enviar_email(email, "Activación de cuenta - CAE Accesible", cuerpo_email):
                flash('Usuario centro creado correctamente. Se ha enviado un email de activación.', 'success')
            else:
                flash('Usuario centro creado pero hubo un error al enviar el email de activación.', 'warning')

            return redirect(url_for('ug_usuarios_centros.usuarios_centros', 
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id, 
                                    centro_id=centro_id
                                    ))

    except Exception as e:
        flash(f'Error al crear el usuario centro: {str(e)}', 'danger')
        return render_template('usuarios_gestores/usuarios_centros/crear.html',
                               gestor_id=gestor_id,
                               nombre_gestor=nombre_gestor,
                               titular=titular,
                               centro=centro,
                               datos_formulario=request.form
                               )

def usuarios_centros_actualizar_vista(gestor_id, titular_id, centro_id, usuario_centro_id):
    return render_template('usuarios_gestores/usuarios_centros/actualizar.html')

def usuarios_centros_eliminar_vista(gestor_id, titular_id, centro_id, usuario_centro_id):
    '''
    Vista para eliminar un usuario-centro de un centro seleccionado
    '''
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id, centro_id)
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_id, gestor, titular, centro = resultado

        # Obtener el usuario-centro a eliminar
        usuario_centro = db.usuarios_centros.find_one({'_id': ObjectId(usuario_centro_id)})
        if not usuario_centro:
            flash('Usuario centro no encontrado', 'danger')
            return redirect(url_for('ug_usuarios_centros.usuarios_centros', 
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id, 
                                    centro_id=centro_id
                                    ))

        # Eliminar el usuario-centro
        result = db.usuarios_centros.delete_one({'_id': ObjectId(usuario_centro_id)})

        if result.deleted_count > 0:
            flash('Usuario-centro eliminado exitosamente', 'success')
            return redirect(url_for('ug_usuarios_centros.usuarios_centros', 
                                 gestor_id=gestor_id, 
                                 titular_id=titular_id, 
                                 centro_id=centro_id
                                 ))
        else:
            flash('No se pudo eliminar el usuario-centro', 'danger')
            return redirect(url_for('ug_usuarios_centros.usuarios_centros', 
                                 gestor_id=gestor_id, 
                                 titular_id=titular_id, 
                                 centro_id=centro_id
                                 ))

    except Exception as e:
        flash(f'Error al eliminar el usuario-centro: {str(e)}', 'danger')
        return redirect(url_for('ug_usuarios_centros.usuarios_centros', 
                                gestor_id=gestor_id, 
                                titular_id=titular_id, 
                                centro_id=centro_id
                                ))

                             
