from datetime import datetime
import re
from flask import request, redirect, url_for, render_template, flash, session
from models.gestores_model import GestoresCollection, UsuariosGestoresCollection
from utils.email_utils import enviar_email
from utils.token_utils import generar_token_verificacion
from utils.usuario_rol_utils import (
    obtener_rol, 
    crear_rol, 
    obtener_usuario_rol, 
    crear_usuario_rol,
    verificar_usuario_existente,
    crear_usuario
)
from config import conexion_mongo
from bson.objectid import ObjectId
# from icecream import ic

db = conexion_mongo()

def registrate_vista():
    
    if request.method == 'POST':
        try:
            # ic("Iniciando proceso de registro")
            # Verificar si el usuario existe
            email = request.form['email'].strip().lower()
            nombre_gestor = request.form['nombre_gestor'].strip().upper()
            nombre_usuario = request.form['alias_usuario_gestor'].strip().upper()
            cif_dni = request.form['cif_dni'].strip().upper()
            domicilio = request.form['domicilio'].strip()
            codigo_postal = request.form['codigo_postal'].strip()
            poblacion = request.form['poblacion'].strip().upper()
            provincia = request.form['provincia'].strip().upper()
            telefono_gestor = request.form['telefono_gestor'].strip()
            telefono_usuario = request.form['telefono_usuario'].strip()
            fecha_actual = datetime.now()

            existe_usuario, usuario_id = verificar_usuario_existente(email)
            
            if existe_usuario:
                # Verificar si ya tiene el rol de gestor
                existe_rol, rol_gestor_id = obtener_rol('gestor')
                if not existe_rol:
                    rol_gestor_id = crear_rol('gestor')
                
                tiene_rol, _ = obtener_usuario_rol(usuario_id, rol_gestor_id)
                
                if tiene_rol:
                    flash("El email ya está registrado como usuario gestor", "danger")
                    return render_template('registrate.html', form_data=request.form)
                else:
                    crear_usuario_rol(usuario_id, rol_gestor_id)
            else:
                # Si el usuario no existe, crear el token de verificación
                token = generar_token_verificacion(email)
                
                # Crear diccionario con los datos del nuevo usuario
                datos_usuario = {
                    'nombre_usuario': nombre_usuario,
                    'telefono_usuario': telefono_usuario,
                    'token_verificacion': token
                }
                
                # Crear el nuevo usuario
                usuario_id = crear_usuario(email, datos_usuario)
                
                # Obtener o crear el rol de gestor
                existe_rol, rol_gestor_id = obtener_rol('gestor')
                if not existe_rol:
                    rol_gestor_id = crear_rol('gestor')
                
                # Crear la relación usuario-rol
                usuario_rol_id = crear_usuario_rol(usuario_id, rol_gestor_id)
                
                # Crear el gestor
                gestor = GestoresCollection(
                    nombre_gestor=nombre_gestor,
                    cif_dni=cif_dni,
                    domicilio=domicilio,
                    codigo_postal=codigo_postal,
                    poblacion=poblacion,
                    provincia=provincia,
                    telefono_gestor=telefono_gestor,
                    fecha_activacion=fecha_actual,
                    fecha_modificacion=fecha_actual,
                    fecha_inactivacion=None,
                    estado_gestor='activo'
                )
                gestor_id = db.gestores.insert_one(gestor.__dict__).inserted_id
                
                # Crear la relación usuario-gestor
                usuario_gestor = UsuariosGestoresCollection(
                    usuario_rol_id=usuario_rol_id,
                    gestor_id=gestor_id,
                    alias_usuario_gestor=nombre_usuario,
                    fecha_activacion=fecha_actual,
                    fecha_modificacion=fecha_actual,
                    fecha_inactivacion=None,
                    estado_usuario_gestor='activo'
                )
                db.usuarios_gestores.insert_one(usuario_gestor.__dict__)
                
                # Enviar email de verificación
                link_verificacion = url_for('verificar_email', token=token, email=email, _external=True)
                
                # Renderizar el template del email
                cuerpo_email = render_template(
                    'emails/registro_gestor.html',
                    nombre_usuario=nombre_usuario,
                    nombre_gestor=nombre_gestor,
                    link_verificacion=link_verificacion
                )
                
                if enviar_email(email, "Activa tu cuenta en CAE Accesible", cuerpo_email):
                    # Guardar token y email en la sesión
                    session['verification_token'] = token
                    session['verification_email'] = email
                    flash("Te hemos enviado un email para activar tu cuenta. Por favor, revisa tu bandeja de entrada o spam.", "success")
                    return redirect(url_for('login'))
                else:
                    flash("Hubo un problema al enviar el email de verificación. Por favor, intenta registrarte nuevamente.", "danger")
                    return render_template('registrate.html', form_data=request.form)
        
        except Exception as e:
            # ic("Error en el registro:", str(e))
            flash(f"Error en el registro: {str(e)}", "danger")
            return render_template('registrate.html', form_data=request.form)
    
    return render_template('registrate.html')
