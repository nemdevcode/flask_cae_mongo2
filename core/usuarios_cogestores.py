from flask import render_template, request, redirect, url_for, session, flash
from bson import ObjectId
from datetime import datetime
import re
from config import conexion_mongo

db = conexion_mongo()

def gestores_usuarios_cogestores_vista():
    
    try:
        # Obtener el ID del gestor actual desde la sesión
        gestor_id = session.get('usuario_id')
        if not gestor_id:
            flash('No hay gestor autenticado', 'error')
            return redirect(url_for('login'))

        # Obtener el nombre del gestor
        gestor = db.usuarios.find_one({'_id': ObjectId(gestor_id)})
        nombre_gestor = gestor.get('nombre_usuario', 'Gestor')

        # Obtener parámetros de filtrado
        filtrar_cogestor = request.form.get('filtrar_cogestor', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('gestores.gestores_usuarios_cogestores'))

        # Construir la consulta base
        query = {'gestor_id': ObjectId(gestor_id)}
        
        # Aplicar filtros si existen
        if filtrar_estado != 'todos':
            query['estado'] = filtrar_estado

        # Obtener los cogestores asociados al gestor
        cogestores = []
        usuarios_cogestores = db.usuarios_cogestores.find(query)
        
        for uc in usuarios_cogestores:
            # Obtener la información del usuario
            usuario = db.usuarios.find_one({'_id': uc['usuario_id']})
            if usuario:
                # Si hay filtro por nombre, verificar si coincide
                if filtrar_cogestor:
                    if (filtrar_cogestor.lower() not in usuario['nombre_usuario'].lower() and 
                        filtrar_cogestor.lower() not in uc['alias'].lower() and
                        filtrar_cogestor.lower() not in usuario['telefono'].lower() and
                        filtrar_cogestor.lower() not in usuario['email'].lower()):
                        continue

                cogestor = {
                    '_id': uc['_id'],
                    'cogestor_info': {
                        'alias': uc['alias'],
                        'estado': uc['estado']
                    },
                    'nombre_usuario': usuario['nombre_usuario'],
                    'telefono': usuario['telefono'],
                    'email': usuario['email']
                }
                cogestores.append(cogestor)

                # Obtener mensaje_ok de los argumentos de la URL si existe
                mensaje_ok = request.args.get('mensaje_ok')

        return render_template('gestores/cogestores/listar.html', 
                             cogestores=cogestores,
                             nombre_gestor=nombre_gestor,
                             filtrar_cogestor=filtrar_cogestor,
                             filtrar_estado=filtrar_estado,
                             mensaje_ok=mensaje_ok)
    except Exception as e:
        flash(f'Error al cargar la lista de cogestores: {str(e)}', 'error')
        return redirect(url_for('gestores.gestores_usuarios_cogestores'))

def gestores_usuarios_cogestores_crear_vista():

    if request.method == 'GET':
        return render_template('gestores/cogestores/crear.html')
    
    if request.method == 'POST':
        try:
            # Obtener el ID del gestor actual
            gestor_id = session.get('usuario_id')
            if not gestor_id:
                flash('No hay gestor autenticado', 'error')
                return redirect(url_for('login'))

            # Obtener datos del formulario
            alias = request.form.get('alias', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '').strip()
            password_confirm = request.form.get('password_confirm', '').strip()
            if password != password_confirm:
                return render_template('gestores/cogestores/crear.html',
                                    mensaje_error='Las contraseñas no coinciden',
                                    form_data=request.form)

            # Verificar si el alias ya existe para este gestor
            if db.usuarios_cogestores.find_one({
                'alias': alias,
                'gestor_id': ObjectId(gestor_id)
            }):
                return render_template('gestores/cogestores/crear.html',
                                    mensaje_error='El alias ya está en uso para este gestor',
                                    form_data=request.form)

            # Verificar si ya existe un cogestor con ese email para este gestor
            usuario_existente = db.usuarios.find_one({'email': email})
            if usuario_existente:
                # Verificar si ya es cogestor de este gestor
                cogestor_existente = db.usuarios_cogestores.find_one({
                    'usuario_id': usuario_existente['_id'],
                    'gestor_id': ObjectId(gestor_id)
                })
                if cogestor_existente:
                    return render_template('gestores/cogestores/crear.html',
                                        mensaje_error='Este usuario ya es cogestor para este gestor',
                                        form_data=request.form)
                
                # Verificar si el usuario ya tiene el rol de cogestor
                rol_cogestor = db.roles.find_one({'nombre_rol': 'cogestor'})
                if rol_cogestor:
                    usuario_rol = db.usuarios_roles.find_one({
                        'usuario_id': usuario_existente['_id'],
                        'rol_id': rol_cogestor['_id']
                    })
                    if not usuario_rol:
                        # Si no tiene el rol, asignarlo
                        usuario_rol_data = {
                            'usuario_id': usuario_existente['_id'],
                            'rol_id': rol_cogestor['_id'],
                            'fecha_alta': datetime.now(),
                            'fecha_modificacion': datetime.now(),
                            'fecha_baja': None,
                            'estado': 'activo'
                        }
                        db.usuarios_roles.insert_one(usuario_rol_data)
                
                # Usar el usuario existente
                usuario_id = usuario_existente['_id']
            else:
                # Crear nuevo usuario
                usuario_data = {
                    'nombre_usuario': '',
                    'email': email,
                    'password': password,
                    'telefono': '',
                    'fecha_alta': datetime.now(),
                    'fecha_modificacion': datetime.now(),
                    'fecha_baja': None,
                    'estado': 'activo'
                }
                resultado_usuario = db.usuarios.insert_one(usuario_data)
                usuario_id = resultado_usuario.inserted_id

                # Obtener o crear el rol de cogestor
                rol_cogestor = db.roles.find_one({'nombre_rol': 'cogestor'})
                if not rol_cogestor:
                    rol_data = {
                        'nombre_rol': 'cogestor',
                        'descripcion': 'Rol de cogestor',
                        'fecha_alta': datetime.now(),
                        'fecha_modificacion': datetime.now(),
                        'fecha_baja': None,
                        'estado': 'activo'
                    }
                    resultado_rol = db.roles.insert_one(rol_data)
                    rol_id = resultado_rol.inserted_id
                else:
                    rol_id = rol_cogestor['_id']

                # Crear la relación usuario-rol
                usuario_rol_data = {
                    'usuario_id': usuario_id,
                    'rol_id': rol_id,
                    'fecha_alta': datetime.now(),
                    'fecha_modificacion': datetime.now(),
                    'fecha_baja': None,
                    'estado': 'activo'
                }
                db.usuarios_roles.insert_one(usuario_rol_data)
            
            # Crear el cogestor
            cogestor_data = {
                'usuario_id': usuario_id,
                'gestor_id': ObjectId(gestor_id),
                'alias': alias,
                'estado': 'activo',
                'fecha_alta': datetime.now(),
                'fecha_modificacion': datetime.now(),
                'fecha_baja': None
            }
            
            # Insertar cogestor
            db.usuarios_cogestores.insert_one(cogestor_data)
            
            # Redireccionar con mensaje de éxito
            return redirect(url_for('gestores.gestores_usuarios_cogestores', 
                                  mensaje_ok='Cogestor creado exitosamente'))
            
        except Exception as e:
            return render_template('gestores/cogestores/crear.html',
                                mensaje_error=str(e),
                                form_data=request.form)

def gestores_usuarios_cogestores_actualizar_vista():
    
    try:
        # Obtener el ID del gestor actual
        gestor_id = session.get('usuario_id')
        if not gestor_id:
            return redirect(url_for('login', mensaje_error='No hay gestor autenticado'))

        # Obtener el ID del cogestor a actualizar
        cogestor_id = request.args.get('cogestor_id')
        if not cogestor_id:
            return redirect(url_for('gestores.gestores_usuarios_cogestores', 
                                  mensaje_error='ID de cogestor no proporcionado'))

        # Verificar que el cogestor pertenece al gestor actual
        cogestor = db.usuarios_cogestores.find_one({
            '_id': ObjectId(cogestor_id),
            'gestor_id': ObjectId(gestor_id)
        })

        if not cogestor:
            return redirect(url_for('gestores.gestores_usuarios_cogestores', 
                                  mensaje_error='Cogestor no encontrado o no pertenece a este gestor'))

        # Obtener la información del usuario
        usuario = db.usuarios.find_one({'_id': cogestor['usuario_id']})
        if not usuario:
            return redirect(url_for('gestores.gestores_usuarios_cogestores', 
                                  mensaje_error='Usuario no encontrado'))

        # Preparar los datos para el template
        cogestor_data = {
            '_id': cogestor['_id'],
            'cogestor_info': {
                'alias': cogestor['alias'],
                'estado': cogestor['estado']
            },
            'email': usuario['email'],
            'password': usuario['password']
        }

        if request.method == 'GET':
            return render_template('gestores/cogestores/actualizar.html', cogestor=cogestor_data)

        if request.method == 'POST':
            # Obtener datos del formulario
            alias = request.form.get('alias', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '').strip()
            password_confirm = request.form.get('password_confirm', '').strip()
            estado = request.form.get('estado', 'activo')

            if password != password_confirm:
                return render_template('gestores/cogestores/actualizar.html',
                                    cogestor=cogestor_data,
                                    mensaje_error='Las contraseñas no coinciden')

            # Verificar si el alias ya existe para este gestor (excluyendo el cogestor actual)
            if db.usuarios_cogestores.find_one({
                'alias': alias,
                'gestor_id': ObjectId(gestor_id),
                '_id': {'$ne': ObjectId(cogestor_id)}
            }):
                return render_template('gestores/cogestores/actualizar.html',
                                    cogestor=cogestor_data,
                                    mensaje_error='El alias ya está en uso para este gestor')

            # Verificar si el email ya existe en otro usuario
            if email != usuario['email']:
                if db.usuarios.find_one({'email': email}):
                    return render_template('gestores/cogestores/actualizar.html',
                                        cogestor=cogestor_data,
                                        mensaje_error='El email ya está en uso por otro usuario')

            # Actualizar el usuario
            db.usuarios.update_one(
                {'_id': usuario['_id']},
                {
                    '$set': {
                        'email': email,
                        'fecha_modificacion': datetime.now()
                    }
                }
            )

            # Actualizar el cogestor
            db.usuarios_cogestores.update_one(
                {'_id': ObjectId(cogestor_id)},
                {
                    '$set': {
                        'alias': alias,
                        'estado': estado,
                        'fecha_modificacion': datetime.now()
                    }
                }
            )

            return redirect(url_for('gestores.gestores_usuarios_cogestores', 
                                  mensaje_ok='Cogestor actualizado exitosamente'))

    except Exception as e:
        return render_template('gestores/cogestores/actualizar.html',
                             cogestor=cogestor_data if 'cogestor_data' in locals() else None,
                             mensaje_error=f'Error al actualizar el cogestor: {str(e)}')

def gestores_usuarios_cogestores_eliminar_vista():
    try:
        # Obtener el ID del gestor actual
        gestor_id = session.get('usuario_id')
        if not gestor_id:
            return redirect(url_for('login', mensaje_error='No hay gestor autenticado'))

        # Obtener el ID del cogestor a eliminar
        cogestor_id = request.args.get('cogestor_id')
        if not cogestor_id:
            return redirect(url_for('gestores.gestores_usuarios_cogestores', 
                                  mensaje_error='ID de cogestor no proporcionado'))

        # Verificar que el cogestor pertenece al gestor actual
        cogestor = db.usuarios_cogestores.find_one({
            '_id': ObjectId(cogestor_id),
            'gestor_id': ObjectId(gestor_id)
        })

        if not cogestor:
            return redirect(url_for('gestores.gestores_usuarios_cogestores', 
                                  mensaje_error='Cogestor no encontrado o no pertenece a este gestor'))

        # Eliminar el cogestor
        db.usuarios_cogestores.delete_one({'_id': ObjectId(cogestor_id)})

        return redirect(url_for('gestores.gestores_usuarios_cogestores', 
                              mensaje_ok='Cogestor eliminado exitosamente'))

    except Exception as e:
        return redirect(url_for('gestores.gestores_usuarios_cogestores', 
                              mensaje_error=f'Error al eliminar el cogestor: {str(e)}'))

def usuarios_cogestores_vista():
    return render_template('cogestores/cogestores.html')

def usuarios_cogestores_gestor_vista():
    return render_template('cogestores/cogestores_gestor.html')


