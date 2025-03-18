from flask import render_template, request, redirect, url_for, session
from bson.objectid import ObjectId
from datetime import datetime
import re

from config import conexion_mongo

db = conexion_mongo()

def usuarios_vista():
    
    usuario_id = session.get('usuario_id')
    usuario = db.usuarios.find_one({'_id': ObjectId(usuario_id)})

    usuario_roles = list(db.usuarios_roles.find({'usuario_id': ObjectId(usuario_id)}))

    # Almacenar los IDs de usuarios_roles en la sesión
    session['usuarios_roles_ids'] = [str(ur['_id']) for ur in usuario_roles]  # Convertir ObjectId a string

    # Extraer los rol_id de la lista
    rol_ids = [ObjectId(ur['rol_id']) for ur in usuario_roles]
    
    # Buscar los nombres de roles en la colección roles
    roles = list(db.roles.find({'_id': {'$in': rol_ids}}, {'nombre_rol': 1}))
    
    # Crear variables en la sesión para cada rol usando el ID del usuario
    for rol in roles:
        nombre_variable = rol['nombre_rol'].lower()  # gestor, admin, etc.
        session[nombre_variable] = str(usuario_id)  # Guardamos el ID del usuario directamente
    
    # Extraer solo los nombres de roles
    nombres_roles = [rol['nombre_rol'].upper() for rol in roles]
    
    # Obtener mensaje_ok de los argumentos de la URL si existe
    mensaje_ok = request.args.get('mensaje_ok')
    
    return render_template('usuarios.html', 
                         usuario=usuario, 
                         nombres_roles=nombres_roles,
                         mensaje_ok=mensaje_ok)
    
def usuario_actualizar_vista():

    if request.method == 'GET':
        usuario_id = session.get('usuario_id')
        usuario = db.usuarios.find_one({'_id': ObjectId(usuario_id)})
        return render_template('usuarios_actualizar.html', usuario=usuario)

    if request.method == 'POST':
        try:
            usuario_id = session.get('usuario_id')
            datos_actualizados = {
                'nombre_usuario': request.form.get('nombre_usuario').strip().upper(),
                'cif_dni': re.sub(r'[^A-Z0-9]', '', request.form.get('cif_dni').strip().upper()),
                'domicilio': request.form.get('domicilio').strip(),
                'codigo_postal': request.form.get('codigo_postal').strip().upper(),
                'poblacion': request.form.get('poblacion').strip().upper(),
                'provincia': request.form.get('provincia').strip().upper(),
                'telefono': request.form.get('telefono').strip(),
                'email': request.form.get('email').strip().lower(),
                'password': request.form.get('password').strip(),
                'confirmar_password': request.form.get('confirmar_password').strip(),
                'fecha_modificacion': datetime.now()
            }

            if datos_actualizados['password'] != datos_actualizados['confirmar_password']:
                usuario_id = session.get('usuario_id')
                usuario = db.usuarios.find_one({'_id': ObjectId(usuario_id)})
                return render_template('usuarios_actualizar.html', 
                                    usuario=usuario, 
                                    mensaje_error='Las contraseñas no coinciden')
            
            # Verificar si el email ya existe en otro usuario
            email_existente = db.usuarios.find_one({
                '_id': {'$ne': ObjectId(usuario_id)},  # Excluir el usuario actual
                'email': datos_actualizados['email']
            })
            
            if email_existente:
                usuario = db.usuarios.find_one({'_id': ObjectId(usuario_id)})
                return render_template('usuarios_actualizar.html', 
                                    usuario=usuario, 
                                    mensaje_error='El email ya está registrado por otro usuario')
            
            db.usuarios.update_one(
                {'_id': ObjectId(usuario_id)},
                {'$set': datos_actualizados}
            )
            
            return redirect(url_for('usuarios.usuarios', mensaje_ok='Usuario actualizado correctamente'))
            
        except Exception as e:
            usuario_id = session.get('usuario_id')
            usuario = db.usuarios.find_one({'_id': ObjectId(usuario_id)})
            return render_template('usuarios_actualizar.html', 
                                usuario=usuario, 
                                mensaje_error=str(e))
