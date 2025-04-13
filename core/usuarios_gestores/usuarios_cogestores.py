from flask import render_template, request, redirect, url_for, session, flash
from bson import ObjectId
from datetime import datetime
from config import conexion_mongo
from utils.token_utils import generar_token_verificacion
from utils.email_utils import enviar_email
from utils.usuario_utils import (
    crear_usuario,
    verificar_usuario_existente
)
from utils.rol_utils import (
    crear_rol,
    obtener_rol
)
from utils.usuario_rol_utils import (
    crear_usuario_rol,
    obtener_usuario_rol
)
from models.usuarios_model import UsuariosCollection
from models.roles_model import RolesCollection
from models.usuarios_roles_model import UsuariosRolesCollection
from models.cogestores_model import UsuariosCogestoresCollection

db = conexion_mongo()

def usuarios_cogestores_vista():
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
            return redirect(url_for('usuarios.usuarios'))

        # Verificar si el usuario tiene el rol de gestor
        tiene_rol, usuario_rol_id = obtener_usuario_rol(usuario_id, rol_gestor_id)
        
        if not tiene_rol:
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        # Obtener la información del usuario
        usuario = db.usuarios.find_one({'_id': ObjectId(usuario_id)})
        
        nombre_gestor = usuario.get('nombre_usuario', 'Gestor')

        # Obtener parámetros de filtrado
        filtrar_cogestor = request.form.get('filtrar_cogestor', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('ug_usuarios_cogestores.usuarios_cogestores'))

        # Construir la consulta base - buscar cogestores donde el usuario_rol_gestor_id sea el del gestor actual
        query = {'usuario_rol_gestor_id': ObjectId(usuario_rol_id)}
        
        # Aplicar filtros si existen
        if filtrar_estado != 'todos':
            query['estado_usuario_cogestor'] = filtrar_estado

        # Obtener los cogestores asociados al gestor
        cogestores = []
        usuarios_cogestores = list(db.usuarios_cogestores.find(query))
        
        for uc in usuarios_cogestores:
            # Obtener el usuario_rol del cogestor usando usuario_rol_id
            usuario_rol = db.usuarios_roles.find_one({'_id': ObjectId(uc['usuario_rol_id'])})
            
            if usuario_rol:
                # Obtener la información del usuario cogestor
                usuario_cogestor = db.usuarios.find_one({'_id': ObjectId(usuario_rol['usuario_id'])})
                
                if usuario_cogestor:
                    # Si hay filtro por nombre, verificar si coincide
                    if filtrar_cogestor:
                        if (filtrar_cogestor.lower() not in uc['alias_usuario_cogestor'].lower() and
                            filtrar_cogestor.lower() not in usuario_cogestor['email'].lower()):
                            continue

                    cogestor = {
                        '_id': uc['_id'],
                        'cogestor_info': {
                            'alias': uc['alias_usuario_cogestor'],
                            'nombre_usuario': usuario_cogestor['nombre_usuario'],
                            'telefono_usuario': usuario_cogestor['telefono_usuario'],
                            'estado_usuario_cogestor': uc['estado_usuario_cogestor']
                        },
                        'email': usuario_cogestor['email']
                    }
                    cogestores.append(cogestor)

        return render_template('usuarios_gestores/usuarios_cogestores/listar.html', 
                             cogestores=cogestores,
                             nombre_gestor=nombre_gestor,
                             filtrar_cogestor=filtrar_cogestor,
                             filtrar_estado=filtrar_estado)

    except Exception as e:
        flash(f'Error al listar los cogestores: {str(e)}', 'danger')
        return redirect(url_for('usuarios.usuarios'))

def crear_usuario_cogestor(usuario_rol_id, usuario_rol_gestor_id, alias):
    """
    Crea un nuevo usuario cogestor
    """
    fecha_actual = datetime.now()
    usuario_cogestor = UsuariosCogestoresCollection(
        usuario_rol_id=usuario_rol_id,
        usuario_rol_gestor_id=usuario_rol_gestor_id,
        alias_usuario_cogestor=alias,
        fecha_activacion=fecha_actual,
        fecha_modificacion=fecha_actual,
        fecha_inactivacion=None,
        estado_usuario_cogestor='activo'
    )
    return db.usuarios_cogestores.insert_one(usuario_cogestor.__dict__)

def usuarios_cogestores_crear_vista():
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
            return redirect(url_for('usuarios.usuarios'))

        # Verificar si el usuario tiene el rol de gestor
        tiene_rol, usuario_rol_id = obtener_usuario_rol(usuario_id, rol_gestor_id)
        
        if not tiene_rol:
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        if request.method == 'GET':
            return render_template('usuarios_gestores/usuarios_cogestores/crear.html')
        
        if request.method == 'POST':
            # Obtener datos del formulario
            email = request.form.get('email', '').strip().lower()
            alias = request.form.get('alias', '').strip().upper()
            
            if not email or not alias:
                flash('El email y el alias son obligatorios', 'danger')
                return render_template('usuarios_gestores/usuarios_cogestores/crear.html',
                                    form_data=request.form)

            # Verificar si el usuario existe
            existe_usuario, usuario_cogestor_id = verificar_usuario_existente(email)
            
            if existe_usuario:
                # Obtener rol de cogestor
                existe_rol, rol_cogestor_id = obtener_rol('cogestor')
                
                if not existe_rol:
                    rol_cogestor_id = crear_rol('cogestor')
                
                # Verificar si el usuario ya tiene el rol de cogestor
                tiene_rol_cogestor, usuario_rol_cogestor_id = obtener_usuario_rol(usuario_cogestor_id, rol_cogestor_id)
                
                if tiene_rol_cogestor:
                    # Verificar si ya es cogestor para este gestor específico
                    cogestor_existente = db.usuarios_cogestores.find_one({
                        'usuario_rol_id': ObjectId(usuario_rol_cogestor_id),
                        'usuario_rol_gestor_id': ObjectId(usuario_rol_id)
                    })
                    
                    if cogestor_existente:
                        flash('Este email ya está registrado como cogestor para este gestor', 'danger')
                        return render_template('usuarios_gestores/usuarios_cogestores/crear.html',
                                            form_data=request.form)
                else:
                    # Si no tiene el rol de cogestor, crearlo
                    usuario_rol_cogestor_id = crear_usuario_rol(usuario_cogestor_id, rol_cogestor_id)
                
                # Crear el cogestor
                crear_usuario_cogestor(usuario_rol_cogestor_id, usuario_rol_id, alias)
                flash('Este email ya está registrado, será asignado como cogestor para este gestor', 'success')
                return redirect(url_for('ug_usuarios_cogestores.usuarios_cogestores'))

            # Si el usuario no existe, crear nuevo usuario y cogestor
            # Generar token de verificación
            token = generar_token_verificacion(email)
            
            # Crear diccionario con los datos del nuevo usuario
            datos_usuario = {
                'token_verificacion': token,
                'verificado': False
            }
            
            # Crear el nuevo usuario
            nuevo_usuario_id = crear_usuario(email, datos_usuario)
            
            # Obtener rol de cogestor y crear usuario_rol
            existe_rol, rol_cogestor_id = obtener_rol('cogestor')
            if not existe_rol:
                rol_cogestor_id = crear_rol('cogestor')
            
            usuario_rol_cogestor_id = crear_usuario_rol(nuevo_usuario_id, rol_cogestor_id)
            
            # Crear el cogestor
            crear_usuario_cogestor(usuario_rol_cogestor_id, usuario_rol_id, alias)

            # Enviar email de verificación solo para usuarios nuevos
            link_verificacion = url_for('verificar_email', token=token, email=email, _external=True)
            cuerpo_email = render_template(
                    'emails/registro_cogestor.html',
                    alias=alias,
                    link_verificacion=link_verificacion
                )

            if enviar_email(email, "Activación de cuenta - CAE Accesible", cuerpo_email):
                flash('Cogestor creado correctamente. Se ha enviado un email de activación.', 'success')
            else:
                flash('Cogestor creado pero hubo un error al enviar el email de activación.', 'warning')

            return redirect(url_for('ug_usuarios_cogestores.usuarios_cogestores'))

    except Exception as e:
        flash(f'Error al crear el cogestor: {str(e)}', 'danger')
        return render_template('usuarios_gestores/usuarios_cogestores/crear.html',
                            form_data=request.form)

def usuarios_cogestores_actualizar_vista():
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
            return redirect(url_for('usuarios.usuarios'))

        # Verificar si el usuario tiene el rol de gestor
        tiene_rol, usuario_rol_id = obtener_usuario_rol(usuario_id, rol_gestor_id)
        if not tiene_rol:
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        # Obtener el ID del cogestor a actualizar
        cogestor_id = request.args.get('cogestor_id')
        if not cogestor_id:
            flash('ID de cogestor no proporcionado', 'danger')
            return redirect(url_for('ug_usuarios_cogestores.usuarios_cogestores'))

        # Verificar que el cogestor pertenece al gestor actual
        cogestor = db.usuarios_cogestores.find_one({
            '_id': ObjectId(cogestor_id),
            'usuario_rol_gestor_id': ObjectId(usuario_rol_id)
        })

        if not cogestor:
            flash('Cogestor no encontrado o no pertenece a este gestor', 'danger')
            return redirect(url_for('ug_usuarios_cogestores.usuarios_cogestores'))

        # Obtener el usuario_rol del cogestor
        usuario_rol = db.usuarios_roles.find_one({'_id': ObjectId(cogestor['usuario_rol_id'])})
        if not usuario_rol:
            flash('Usuario rol no encontrado', 'danger')
            return redirect(url_for('ug_usuarios_cogestores.usuarios_cogestores'))

        # Obtener la información del usuario cogestor
        usuario = db.usuarios.find_one({'_id': ObjectId(usuario_rol['usuario_id'])})
        if not usuario:
            flash('Usuario no encontrado', 'danger')
            return redirect(url_for('ug_usuarios_cogestores.usuarios_cogestores'))

        # Preparar los datos para el template
        cogestor_data = {
            '_id': cogestor['_id'],
            'cogestor_info': {
                'alias': cogestor['alias_usuario_cogestor'],
                'estado_usuario_cogestor': cogestor['estado_usuario_cogestor']
            },
            'email': usuario['email']
        }

        if request.method == 'GET':
            return render_template('usuarios_gestores/usuarios_cogestores/actualizar.html', 
                                cogestor=cogestor_data)

        if request.method == 'POST':
            # Obtener datos del formulario
            alias = request.form.get('alias', '').strip().upper()
            estado = request.form.get('estado', 'activo')

            # Verificar si el alias ya existe para este gestor (excluyendo el cogestor actual)
            if db.usuarios_cogestores.find_one({
                'alias_usuario_cogestor': alias,
                'usuario_rol_gestor_id': ObjectId(usuario_rol_id),
                '_id': {'$ne': ObjectId(cogestor_id)}
            }):
                flash('El alias ya está en uso para este gestor', 'danger')
                return render_template('usuarios_gestores/usuarios_cogestores/actualizar.html',
                                    cogestor=cogestor_data)

            # Actualizar el cogestor
            db.usuarios_cogestores.update_one(
                {'_id': ObjectId(cogestor_id)},
                {
                    '$set': {
                        'alias_usuario_cogestor': alias,
                        'estado_usuario_cogestor': estado,
                        'fecha_modificacion': datetime.now()
                    }
                }
            )

            flash('Cogestor actualizado exitosamente', 'success')
            return redirect(url_for('ug_usuarios_cogestores.usuarios_cogestores'))

    except Exception as e:
        flash(f'Error al actualizar el cogestor: {str(e)}', 'danger')
        return render_template('usuarios_gestores/usuarios_cogestores/actualizar.html',
                             cogestor=cogestor_data if 'cogestor_data' in locals() else None)

def usuarios_cogestores_eliminar_vista():
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
            return redirect(url_for('usuarios.usuarios'))

        # Verificar si el usuario tiene el rol de gestor
        tiene_rol, usuario_rol_id = obtener_usuario_rol(usuario_id, rol_gestor_id)
        if not tiene_rol:
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        # Obtener el ID del cogestor a eliminar
        cogestor_id = request.args.get('cogestor_id')
        if not cogestor_id:
            flash('ID de cogestor no proporcionado', 'danger')
            return redirect(url_for('ug_usuarios_cogestores.usuarios_cogestores'))

        # Verificar que el cogestor pertenece al gestor actual
        cogestor = db.usuarios_cogestores.find_one({
            '_id': ObjectId(cogestor_id),
            'usuario_rol_gestor_id': ObjectId(usuario_rol_id)
        })

        if not cogestor:
            flash('Cogestor no encontrado o no pertenece a este gestor', 'danger')
            return redirect(url_for('ug_usuarios_cogestores.usuarios_cogestores'))

        # Obtener el usuario_rol del cogestor
        usuario_rol = db.usuarios_roles.find_one({'_id': ObjectId(cogestor['usuario_rol_id'])})
        if not usuario_rol:
            flash('Usuario rol no encontrado', 'danger')
            return redirect(url_for('ug_usuarios_cogestores.usuarios_cogestores'))

        # Obtener la información del usuario cogestor
        usuario = db.usuarios.find_one({'_id': ObjectId(usuario_rol['usuario_id'])})
        if not usuario:
            flash('Usuario no encontrado', 'danger')
            return redirect(url_for('ug_usuarios_cogestores.usuarios_cogestores'))

        # Eliminar el cogestor
        db.usuarios_cogestores.delete_one({'_id': ObjectId(cogestor_id)})

        # Verificar si el usuario tiene otros roles
        otros_roles = db.usuarios_roles.find({
            'usuario_id': ObjectId(usuario_rol['usuario_id']),
            '_id': {'$ne': ObjectId(usuario_rol['_id'])}
        }).count()

        # Si no tiene otros roles, eliminar el usuario_rol
        if otros_roles == 0:
            db.usuarios_roles.delete_one({'_id': ObjectId(usuario_rol['_id'])})

        flash('Cogestor eliminado exitosamente', 'success')
        return redirect(url_for('ug_usuarios_cogestores.usuarios_cogestores'))

    except Exception as e:
        flash(f'Error al eliminar el cogestor: {str(e)}', 'danger')
        return redirect(url_for('ug_usuarios_cogestores.usuarios_cogestores'))

# def usuarios_cogestores_vista():
#     try:
#         # Obtener el ID del usuario actual
#         usuario_id = session.get('usuario_id')
#         if not usuario_id:
#             flash('No hay usuario autenticado', 'danger')
#             return redirect(url_for('login'))

#         # Obtener el rol de cogestor
#         existe_rol, rol_cogestor_id = obtener_rol('cogestor')
#         if not existe_rol:
#             flash('Rol de cogestor no encontrado', 'danger')
#             return redirect(url_for('usuarios.usuarios'))

#         # Verificar si el usuario tiene el rol de cogestor
#         tiene_rol, usuario_rol_id = obtener_usuario_rol(usuario_id, rol_cogestor_id)
#         if not tiene_rol:
#             flash('No tienes permisos para acceder a esta página', 'danger')
#             return redirect(url_for('usuarios.usuarios'))

#         # Obtener la información del usuario
#         usuario = db.usuarios.find_one({'_id': ObjectId(usuario_id)})
#         if not usuario:
#             flash('Usuario no encontrado', 'danger')
#             return redirect(url_for('usuarios.usuarios'))

#         nombre_cogestor = usuario.get('nombre_usuario', 'Cogestor')

#         # Obtener parámetros de filtrado
#         filtrar_gestor = request.form.get('filtrar_gestor', '')
#         filtrar_estado = request.form.get('filtrar_estado', 'todos')
#         vaciar = request.args.get('vaciar', '0')

#         # Si se solicita vaciar filtros
#         if vaciar == '1':
#             return redirect(url_for('cogestores.usuarios_cogestores'))

#         # Construir la consulta base - buscar gestores donde el usuario_rol_id sea el del cogestor actual
#         query = {'usuario_rol_id': ObjectId(usuario_rol_id)}
        
#         # Aplicar filtros si existen
#         if filtrar_estado != 'todos':
#             query['estado_usuario_cogestor'] = filtrar_estado

#         # Obtener los gestores asociados al cogestor
#         gestores = []
#         usuarios_cogestores = list(db.usuarios_cogestores.find(query))
        
#         for uc in usuarios_cogestores:
#             # Obtener el usuario_rol del gestor
#             usuario_rol_gestor = db.usuarios_roles.find_one({'_id': ObjectId(uc['usuario_rol_gestor_id'])})
#             if not usuario_rol_gestor:
#                 continue

#             # Obtener la información del usuario gestor
#             usuario_gestor = db.usuarios.find_one({'_id': ObjectId(usuario_rol_gestor['usuario_id'])})
#             if not usuario_gestor:
#                 continue

#             # Si hay filtro por nombre, verificar si coincide
#             if filtrar_gestor:
#                 if (filtrar_gestor.lower() not in uc['alias_usuario_cogestor'].lower() and
#                     filtrar_gestor.lower() not in usuario_gestor['email'].lower() and
#                     filtrar_gestor.lower() not in usuario_gestor['nombre_usuario'].lower() and
#                     filtrar_gestor.lower() not in usuario_gestor['telefono_usuario'].lower()):
#                     continue

#             gestor = {
#                 '_id': uc['_id'],
#                 'gestor_info': {
#                     'alias': uc['alias_usuario_cogestor'],
#                     'nombre_usuario': usuario_gestor['nombre_usuario'],
#                     'telefono_usuario': usuario_gestor['telefono_usuario'],
#                     'estado': uc['estado_usuario_cogestor']
#                 },
#                 'email': usuario_gestor['email']
#             }
#             gestores.append(gestor)

#         return render_template('usuarios/usuarios_cogestores.html', 
#                              gestores=gestores,
#                              nombre_cogestor=nombre_cogestor,
#                              filtrar_gestor=filtrar_gestor,
#                              filtrar_estado=filtrar_estado)

#     except Exception as e:
#         flash(f'Error al listar los gestores: {str(e)}', 'danger')
#         return redirect(url_for('usuarios.usuarios'))

# def usuarios_cogestores_gestor_vista():
#     return render_template('cogestores/cogestores_gestor.html')


