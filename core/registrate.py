from datetime import datetime
import re
from flask import request, redirect, url_for, render_template, flash, session
from models.usuarios_model import UsuariosCollection
from models.roles_model import RolesCollection
from models.usuarios_roles_model import UsuariosRolesCollection
from utils.email_utils import enviar_email
from utils.token_utils import generar_token_verificacion
from config import conexion_mongo
from bson.objectid import ObjectId
# from icecream import ic

db = conexion_mongo()

def registrate_vista():
    
    if request.method == 'POST':
        try:
            # ic("Iniciando proceso de registro")
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
            nombre_rol = 'gestor'
            descripcion = 'Gestor de coordinación'
            
            # ic(f"Datos recibidos - Email: {email}, Nombre: {nombre_usuario}")
            
            # Verificar si el usuario existe
            usuario_existente = db.usuarios.find_one({'email': email})
            
            if usuario_existente:
                # ic("Usuario existente encontrado")
                usuario_id = usuario_existente['_id']
                
                # Verificar si ya tiene el rol de gestor
                rol_gestor = db.roles.find_one({'nombre_rol': 'gestor'})
                if not rol_gestor:
                    # ic("Creando rol gestor")
                    rol = RolesCollection(nombre_rol, descripcion, fecha_alta, fecha_modificacion, fecha_baja, estado='activo')
                    resultado_rol = db.roles.insert_one(rol.__dict__)
                    rol_gestor_id = resultado_rol.inserted_id
                else:
                    rol_gestor_id = rol_gestor['_id']
                
                # Verificar si ya tiene el rol de gestor asignado
                usuario_rol_existente = db.usuarios_roles.find_one({
                    'usuario_id': usuario_id,
                    'rol_id': rol_gestor_id
                })
                
                if usuario_rol_existente:
                    # ic("Usuario ya tiene rol de gestor")
                    flash("El email ya está registrado como gestor", "danger")
                    return render_template('registrate.html', form_data=request.form)
                else:
                    # ic("Creando nueva relación usuario-rol gestor")
                    usuario_rol = UsuariosRolesCollection(
                        usuario_id=usuario_id,
                        rol_id=rol_gestor_id,
                        fecha_alta=fecha_alta,
                        fecha_modificacion=fecha_modificacion,
                        fecha_baja=fecha_baja,
                        estado='activo'
                    )
                    db.usuarios_roles.insert_one(usuario_rol.__dict__)
            else:
                # ic("Creando nuevo usuario")
                # Generar token de verificación
                token = generar_token_verificacion(email)
                
                # Crear nuevo usuario
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
                    estado='pendiente',
                    token_verificacion=token
                )
                
                resultado_usuario = db.usuarios.insert_one(usuario.__dict__)
                usuario_id = resultado_usuario.inserted_id
                
                # Verificar si el rol gestor existe
                rol_gestor = db.roles.find_one({'nombre_rol': 'gestor'})
                if not rol_gestor:
                    # ic("Creando rol gestor")
                    rol = RolesCollection(nombre_rol, descripcion, fecha_alta, fecha_modificacion, fecha_baja, estado='activo')
                    resultado_rol = db.roles.insert_one(rol.__dict__)
                    rol_gestor_id = resultado_rol.inserted_id
                else:
                    rol_gestor_id = rol_gestor['_id']
                
                # Crear relación usuario-rol
                usuario_rol = UsuariosRolesCollection(
                    usuario_id=usuario_id,
                    rol_id=rol_gestor_id,
                    fecha_alta=fecha_alta,
                    fecha_modificacion=fecha_modificacion,
                    fecha_baja=fecha_baja,
                    estado='activo'
                )
                db.usuarios_roles.insert_one(usuario_rol.__dict__)
                
                # Enviar email de verificación
                link_verificacion = url_for('verificar_email', token=token, email=email, _external=True)
                cuerpo_email = f"""
                <h2>Bienvenido a CAE Accesible</h2>
                <p>Gracias por registrarte. Para completar tu registro, por favor, haz clic en el siguiente enlace:</p>
                <p><a href="{link_verificacion}">Activar mi cuenta</a></p>
                <p>Este enlace expirará en 1 hora.</p>
                """
                
                if enviar_email(email, "Activa tu cuenta en CAE Accesible", cuerpo_email):
                    # Guardar token y email en la sesión
                    session['verification_token'] = token
                    session['verification_email'] = email
                    flash("Te hemos enviado un email para activar tu cuenta. Por favor, revisa tu bandeja de entrada.", "success")
                    return redirect(url_for('login'))
                else:
                    flash("Hubo un problema al enviar el email de verificación. Por favor, intenta registrarte nuevamente.", "danger")
                    return render_template('registrate.html', form_data=request.form)
        
        except Exception as e:
            # ic("Error en el registro:", str(e))
            flash(f"Error en el registro: {str(e)}", "danger")
            return render_template('registrate.html', form_data=request.form)
    
    return render_template('registrate.html')
