from flask import render_template, request, redirect, url_for, session
from bson import ObjectId
from datetime import datetime
from config import conexion_mongo

db = conexion_mongo()

def gestores_usuarios_titulares_vista():
    
    try:
        # Obtener el ID del gestor actual desde la sesión
        gestor_id = session.get('usuario_id')
        if not gestor_id:
            return redirect(url_for('login', mensaje_error='No hay gestor autenticado'))

        # Obtener el nombre del gestor
        gestor = db.usuarios.find_one({'_id': ObjectId(gestor_id)})
        nombre_gestor = gestor.get('nombre_usuario', 'Gestor')

        # Obtener parámetros de filtrado
        filtrar_titular = request.form.get('filtrar_titular', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('gestores.gestores_usuarios_titulares'))

        # Construir la consulta base
        query = {'gestor_id': ObjectId(gestor_id)}
        
        # Aplicar filtros si existen
        if filtrar_estado != 'todos':
            query['estado'] = filtrar_estado

        # Obtener los titulares asociados al gestor
        titulares = []
        usuarios_titulares = db.usuarios_titulares.find(query)
        
        for ut in usuarios_titulares:
            # Obtener la información del usuario
            usuario = db.usuarios.find_one({'_id': ut['usuario_id']})
            if usuario:
                # Si hay filtro por nombre, verificar si coincide
                if filtrar_titular:
                    if (filtrar_titular.lower() not in usuario['nombre_usuario'].lower() and 
                        filtrar_titular.lower() not in ut['alias'].lower() and
                        filtrar_titular.lower() not in usuario['telefono'].lower() and
                        filtrar_titular.lower() not in usuario['email'].lower()):
                        continue

                titular = {
                    '_id': ut['_id'],
                    'titular_info': {
                        'alias': ut['alias'],
                        'estado': ut['estado']
                    },
                    'nombre_usuario': usuario['nombre_usuario'],
                    'telefono': usuario['telefono'],
                    'email': usuario['email']
                }
                titulares.append(titular)

                # Obtener mensaje_ok de los argumentos de la URL si existe
                mensaje_ok = request.args.get('mensaje_ok')

        return render_template('gestores/titulares/listar.html', 
                             titulares=titulares,
                             nombre_gestor=nombre_gestor,
                             filtrar_titular=filtrar_titular,
                             filtrar_estado=filtrar_estado,
                             mensaje_ok=mensaje_ok)
    except Exception as e:
        return redirect(url_for('gestores.gestores_usuarios_titulares', mensaje_error=str(e)))

def gestores_usuarios_titulares_crear_vista():

    if request.method == 'GET':
        return render_template('gestores/titulares/crear.html')
    
    if request.method == 'POST':
        try:
            # Obtener el ID del gestor actual
            gestor_id = session.get('usuario_id')
            if not gestor_id:
                return redirect(url_for('login', mensaje_error='No hay gestor autenticado'))

            # Obtener datos del formulario
            alias = request.form.get('alias', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '').strip()
            password_confirm = request.form.get('password_confirm', '').strip()
            if password != password_confirm:
                return render_template('gestores/titulares/crear.html',
                                    mensaje_error='Las contraseñas no coinciden',
                                    form_data=request.form)

            # Verificar si el alias ya existe para este gestor
            if db.usuarios_titulares.find_one({
                'alias': alias,
                'gestor_id': ObjectId(gestor_id)
            }):
                return render_template('gestores/titulares/crear.html',
                                    mensaje_error='El alias ya está en uso para este gestor',
                                    form_data=request.form)

            # Verificar si ya existe un titular con ese email para este gestor
            usuario_existente = db.usuarios.find_one({'email': email})
            if usuario_existente:
                # Verificar si ya es titular de este gestor
                titular_existente = db.usuarios_titulares.find_one({
                    'usuario_id': usuario_existente['_id'],
                    'gestor_id': ObjectId(gestor_id)
                })
                if titular_existente:
                    return render_template('gestores/titulares/crear.html',
                                        mensaje_error='Este usuario ya es titular para este gestor',
                                        form_data=request.form)
                
                # Verificar si el usuario ya tiene el rol de titular
                rol_titular = db.roles.find_one({'nombre_rol': 'titular'})
                if rol_titular:
                    usuario_rol = db.usuarios_roles.find_one({
                        'usuario_id': usuario_existente['_id'],
                        'rol_id': rol_titular['_id']
                    })
                    if not usuario_rol:
                        # Si no tiene el rol, asignarlo
                        usuario_rol_data = {
                            'usuario_id': usuario_existente['_id'],
                            'rol_id': rol_titular['_id'],
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

                # Obtener o crear el rol de titular
                rol_titular = db.roles.find_one({'nombre_rol': 'titular'})
                if not rol_titular:
                    rol_data = {
                        'nombre_rol': 'titular',
                        'descripcion': 'Rol de titular',
                        'fecha_alta': datetime.now(),
                        'fecha_modificacion': datetime.now(),
                        'fecha_baja': None,
                        'estado': 'activo'
                    }
                    resultado_rol = db.roles.insert_one(rol_data)
                    rol_id = resultado_rol.inserted_id
                else:
                    rol_id = rol_titular['_id']

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
            
            # Crear el titular
            titular_data = {
                'usuario_id': usuario_id,
                'gestor_id': ObjectId(gestor_id),
                'alias': alias,
                'estado': 'activo',
                'fecha_alta': datetime.now(),
                'fecha_modificacion': datetime.now(),
                'fecha_baja': None
            }
            
            # Insertar titular
            db.usuarios_titulares.insert_one(titular_data)
            
            # Redireccionar con mensaje de éxito
            return redirect(url_for('gestores.gestores_usuarios_titulares', 
                                  mensaje_ok='Titular creado exitosamente'))
            
        except Exception as e:
            return render_template('gestores/titulares/crear.html',
                                mensaje_error=str(e),
                                form_data=request.form)

def gestores_usuarios_titulares_actualizar_vista():
    return render_template('gestores_usuarios_titulares_actualizar.html')

def gestores_usuarios_titulares_eliminar_vista():
    return render_template('gestores_usuarios_titulares_eliminar.html')

def usuarios_titulares_vista():
    return render_template('usuarios_titulares.html')

def usuarios_titulares_gestor_vista():
    return render_template('usuarios_titulares_gestor.html')