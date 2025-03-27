from datetime import datetime
import re
from flask import request, redirect, url_for, render_template, flash, session
from models.usuarios_model import UsuariosCollection
from models.roles_model import RolesCollection
from models.usuarios_roles_model import UsuariosRolesCollection
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
            existe_usuario, usuario_id = verificar_usuario_existente(email)
            
            if existe_usuario:
                # Verificar si ya tiene el rol de gestor
                existe_rol, rol_gestor_id = obtener_rol('gestor')
                if not existe_rol:
                    rol_gestor_id = crear_rol('gestor')
                
                tiene_rol, _ = obtener_usuario_rol(usuario_id, rol_gestor_id)
                
                if tiene_rol:
                    flash("El email ya está registrado como gestor", "danger")
                    return render_template('registrate.html', form_data=request.form)
                else:
                    crear_usuario_rol(usuario_id, rol_gestor_id)
            else:
                # Si el usuario no existe, preparar datos para crear usuario
                nombre_usuario = request.form['nombre_usuario'].strip().upper()
                telefono = request.form['telefono'].strip()
                email = request.form['email'].strip().lower()
                token = generar_token_verificacion(email)
                
                # Crear diccionario con los datos del nuevo usuario
                datos_usuario = {
                    'nombre_usuario': nombre_usuario,
                    'telefono': telefono,
                    'token_verificacion': token
                }
                
                # Crear el nuevo usuario
                usuario_id = crear_usuario(email, datos_usuario)
                
                # Obtener o crear el rol de gestor
                existe_rol, rol_gestor_id = obtener_rol('gestor')
                if not existe_rol:
                    rol_gestor_id = crear_rol('gestor')
                
                # Crear la relación usuario-rol
                crear_usuario_rol(usuario_id, rol_gestor_id)
                
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
