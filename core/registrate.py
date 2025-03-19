from datetime import datetime
import re
from flask import request, redirect, url_for, render_template
from models.usuarios_model import UsuariosCollection
from models.roles_model import RolesCollection
from models.usuarios_roles_model import UsuariosRolesCollection
from config import conexion_mongo

db = conexion_mongo()

def registrate_vista():
    
    if request.method == 'POST':
        try:
            nombre_usuario = request.form['nombre_usuario'].strip().upper()
            cif_dni = re.sub(r'[^A-Z0-9]', '', request.form.get('cif_dni').strip().upper())
            domicilio = request.form['domicilio'].strip().capitalize()
            codigo_postal = request.form['codigo_postal'].strip().upper()
            poblacion = request.form['poblacion'].strip().upper()
            provincia = request.form['provincia'].strip().upper()
            telefono = request.form['telefono'].strip()
            email = request.form['email'].strip().lower()
            password = request.form['password'].strip()
            password_confirm = request.form['password_confirm'].strip()
            fecha_alta = datetime.now()
            fecha_modificacion = datetime.now()
            fecha_baja = None
            estado = 'activo'
            nombre_rol = 'gestor'
            descripcion = 'Gestor de coordinación'

            if password != password_confirm:
                mensaje_error = "Las contraseñas no coinciden"
                return render_template('registrate.html', 
                                    mensaje_error=mensaje_error,
                                    form_data=request.form)  # Enviamos los datos del formulario
            
            # Listar todos los roles para ver qué hay en la base de datos
            todos_roles = list(db.roles.find())
            # Verificar si el rol ya existe
            rol_existente = db.roles.find_one({'nombre_rol': nombre_rol})
            if rol_existente:
                # Si existe, usar el ID del rol existente
                rol_id = rol_existente['_id']
            else:
                # Si no existe, crear nuevo rol
                rol = RolesCollection(nombre_rol, descripcion, fecha_alta, fecha_modificacion, fecha_baja, estado)
                resultado_rol = db.roles.insert_one(rol.__dict__)
                rol_id = resultado_rol.inserted_id

            # Verificar si el usuario ya existe
            usuario_existente = db.usuarios.find_one({'email': email})
            if usuario_existente:
                usuario_id = usuario_existente['_id']

            else:
                usuario = UsuariosCollection(nombre_usuario, cif_dni, domicilio, codigo_postal, poblacion, 
                                       provincia, telefono, email, password, fecha_alta, 
                                       fecha_modificacion, fecha_baja, estado)
                resultado_usuario = db.usuarios.insert_one(usuario.__dict__) # __dict__ -> Convierte todos los atributos de la clase en un diccionario
                usuario_id = resultado_usuario.inserted_id

            # Verifficar si el usuario ya tiene el rol de gestor
            usuario_rol_existente = db.usuarios_roles.find_one({'usuario_id': usuario_id, 'rol_id': rol_id})
            if usuario_rol_existente:
                mensaje_error = "El email esta registrado debe utilizar otro email para registrarse"
                return render_template('registrate.html', 
                                    mensaje_error=mensaje_error,
                                    form_data=request.form)  # Enviamos los datos del formulario
                
            else:
                usuario_rol = UsuariosRolesCollection(usuario_id, rol_id, fecha_alta, fecha_modificacion, fecha_baja, estado)
                db.usuarios_roles.insert_one(usuario_rol.__dict__) # __dict__ -> Convierte todos los atributos de la clase en un diccionario
                return redirect(url_for('login'))
        
        except Exception as e:
            return render_template('registrate.html', 
                                mensaje_error=f"Error al registrar el usuario: {e}",
                                form_data=request.form)  # Enviamos los datos del formulario
        
    return render_template('registrate.html')
