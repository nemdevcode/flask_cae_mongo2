from flask import render_template, request, redirect, url_for, session
from bson import ObjectId
from datetime import datetime
import re
from config import conexion_mongo

db = conexion_mongo()

def gestores_usuarios_cogestores_vista():
    return render_template('gestores/gestores_cogestores.html')

def gestores_usuarios_cogestores_crear_vista():
    if request.method == 'GET':
        return render_template('gestores/gestores_usuarios_cogestores_crear.html')
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            alias = request.form.get('alias', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '').strip()
            nombre = request.form.get('nombre', '').strip().upper()
            telefono = request.form.get('telefono', '').strip()

            # Verificar si el email ya existe
            if db.usuarios.find_one({'email': email}):
                return render_template('gestores/gestores_usuarios_cogestores_crear.html',
                                    mensaje_error='El email ya está registrado',
                                    form_data=request.form)
            
            # Verificar si el alias ya existe
            if db.cogestores.find_one({'alias': alias}):
                return render_template('gestores/gestores_usuarios_cogestores_crear.html',
                                    mensaje_error='El alias ya está en uso',
                                    form_data=request.form)

            # Crear el usuario
            usuario_data = {
                'nombre_usuario': nombre,
                'email': email,
                'password': password,
                'telefono': telefono,
                'fecha_alta': datetime.now(),
                'fecha_modificacion': datetime.now(),
                'fecha_baja': None
            }
            
            # Insertar usuario
            resultado_usuario = db.usuarios.insert_one(usuario_data)
            usuario_id = resultado_usuario.inserted_id
            
            # Crear el cogestor
            cogestor_data = {
                'usuario_id': usuario_id,
                'alias': alias,
                'estado': 'activo',
                'fecha_alta': datetime.now(),
                'fecha_modificacion': datetime.now(),
                'fecha_baja': None
            }
            
            # Insertar cogestor
            db.cogestores.insert_one(cogestor_data)
            
            # Obtener el ID del rol de cogestor
            rol_cogestor = db.roles.find_one({'nombre_rol': 'cogestor'})
            if not rol_cogestor:
                # Si no existe el rol, crearlo
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
                'fecha_baja': None
            }
            
            # Insertar relación usuario-rol
            db.usuarios_roles.insert_one(usuario_rol_data)
            
            # Redireccionar con mensaje de éxito
            return redirect(url_for('gestores.gestores_usuarios_cogestores', 
                                  mensaje_ok='Cogestor creado exitosamente'))
            
        except Exception as e:
            # En caso de error, mostrar el formulario con el mensaje de error
            return render_template('gestores/gestores_usuarios_cogestores_crear.html',
                                mensaje_error=str(e),
                                form_data=request.form)

def gestores_usuarios_cogestores_actualizar_vista():
    return render_template('gestores/gestores_usuarios_cogestores_actualizar.html')

def gestores_usuarios_cogestores_eliminar_vista():
    return render_template('gestores/gestores_usuarios_cogestores_eliminar.html')

def usuarios_cogestores_vista():
    return render_template('cogestores/cogestores.html')

def usuarios_cogestores_gestor_vista():
    return render_template('cogestores/cogestores_gestor.html')


