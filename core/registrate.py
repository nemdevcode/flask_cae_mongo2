from datetime import datetime
import re
from flask import request, redirect, url_for, render_template, flash, session
from models.usuarios_model import UsuariosCollection
from models.roles_model import RolesCollection
from models.usuarios_roles_model import UsuariosRolesCollection
from utils.email_utils import enviar_email
from utils.token_utils import generar_token_verificacion
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
            fecha_alta = datetime.now()
            fecha_modificacion = datetime.now()
            fecha_baja = None
            estado = 'pendiente'
            nombre_rol = 'gestor'
            descripcion = 'Gestor de coordinación'

            # Verificar si el usuario ya existe
            usuario_existente = db.usuarios.find_one({'email': email})
            if usuario_existente:
                flash("El email ya está registrado", "danger")
                return render_template('registrate.html', form_data=request.form)

            # Generar token de verificación
            token = generar_token_verificacion(email)

            # Primero intentar enviar el email
            link_verificacion = url_for('verificar_email', token=token, email=email, _external=True)
            cuerpo_email = f"""
            <h2>Bienvenido a CAE Accesible</h2>
            <p>Gracias por registrarte. Para completar tu registro, por favor, haz clic en el siguiente enlace:</p>
            <p><a href="{link_verificacion}">Activar mi cuenta</a></p>
            <p>Este enlace expirará en 1 hora.</p>
            """
            
            # Solo proceder con la creación del usuario si el email se envía correctamente
            if enviar_email(email, "Activa tu cuenta en CAE Accesible", cuerpo_email):
                # Crear nuevo usuario sin contraseña
                usuario = UsuariosCollection(
                    nombre_usuario=nombre_usuario,
                    cif_dni=cif_dni,
                    domicilio=domicilio,
                    codigo_postal=codigo_postal,
                    poblacion=poblacion,
                    provincia=provincia,
                    telefono=telefono,
                    email=email,
                    fecha_alta=fecha_alta,
                    fecha_modificacion=fecha_modificacion,
                    fecha_baja=fecha_baja,
                    estado=estado,
                    token_verificacion=token
                )
                
                resultado_usuario = db.usuarios.insert_one(usuario.__dict__)
                usuario_id = resultado_usuario.inserted_id

                # Verificar si el rol ya existe
                rol_existente = db.roles.find_one({'nombre_rol': nombre_rol})
                if rol_existente:
                    rol_id = rol_existente['_id']
                else:
                    rol = RolesCollection(nombre_rol, descripcion, fecha_alta, fecha_modificacion, fecha_baja, estado)
                    resultado_rol = db.roles.insert_one(rol.__dict__)
                    rol_id = resultado_rol.inserted_id

                # Crear relación usuario-rol
                usuario_rol = UsuariosRolesCollection(usuario_id, rol_id, fecha_alta, fecha_modificacion, fecha_baja, estado)
                db.usuarios_roles.insert_one(usuario_rol.__dict__)

                # Guardar token y email en la sesión
                session['verification_token'] = token
                session['verification_email'] = email
                flash("Te hemos enviado un email para activar tu cuenta. Por favor, revisa tu bandeja de entrada.", "success")
                return redirect(url_for('login'))
            else:
                flash("Hubo un problema al enviar el email de verificación. Por favor, intenta registrarte nuevamente.", "danger")
                return render_template('registrate.html', form_data=request.form)
        
        except Exception as e:
            flash(f"Error al registrar el usuario: {e}", "danger")
            return render_template('registrate.html', form_data=request.form)
        
    return render_template('registrate.html')
