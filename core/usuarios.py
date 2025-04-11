from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from datetime import datetime
import re

from utils.token_utils import generar_token_verificacion
from utils.email_utils import enviar_email
from utils.usuario_rol_utils import obtener_roles_usuario
from utils.usuario_utils import obtener_usuario_autenticado, verificar_usuario_existente

from config import conexion_mongo

db = conexion_mongo()

def usuarios_vista():
    """
    Vista principal de usuarios que muestra la información del usuario autenticado y sus roles
    """
    try:
        # Obtener usuario autenticado y verificar permisos
        usuario, respuesta_redireccion = obtener_usuario_autenticado()
        if respuesta_redireccion:
            return respuesta_redireccion

        # Obtener los roles del usuario usando la función de utilidad
        nombres_roles = obtener_roles_usuario(usuario['_id'])
        
        if not nombres_roles:
            flash('No se encontraron roles asociados al usuario', 'warning')

        return render_template('usuarios/index.html',
                             usuario_actual=usuario,
                             nombres_roles=nombres_roles)

    except Exception as e:
        flash(f'Error al cargar la vista de usuarios: {str(e)}', 'danger')
        return redirect(url_for('login'))
    
def usuario_actualizar_vista():
    """
    Vista para actualizar los datos del usuario autenticado
    """
    try:
        # Obtener usuario autenticado
        usuario, respuesta_redireccion = obtener_usuario_autenticado()
        if respuesta_redireccion:
            return respuesta_redireccion

        if request.method == 'GET':
            return render_template('usuarios_actualizar.html', usuario=usuario)

        if request.method == 'POST':
            email = request.form.get('email').strip().lower()
            
            # Verificar si el email ya existe en otro usuario
            existe_usuario, otro_usuario_id = verificar_usuario_existente(email)
            
            if existe_usuario and otro_usuario_id != usuario['_id']:
                flash('El email ya está registrado por otro usuario', 'danger')
                return render_template('usuarios_actualizar.html', usuario=usuario)
            
            # Actualizar datos del usuario
            datos_actualizados = {
                'nombre_usuario': request.form.get('nombre_usuario').strip().upper(),
                'telefono_usuario': request.form.get('telefono_usuario').strip(),
                'email': email,
                'fecha_modificacion': datetime.now()
            }
            
            db.usuarios.update_one(
                {'_id': usuario['_id']},
                {'$set': datos_actualizados}
            )
            
            flash('Usuario actualizado correctamente', 'success')
            return redirect(url_for('usuarios.usuarios'))
            
    except Exception as e:
        flash(f'Error al actualizar el usuario: {str(e)}', 'danger')
        return render_template('usuarios_actualizar.html', usuario=usuario)

def usuario_solicitar_cambio_password():
    try:
        # Obtener usuario autenticado
        usuario, respuesta_redireccion = obtener_usuario_autenticado()
        if respuesta_redireccion:
            return respuesta_redireccion

        email = usuario['email']

        # Generar token de recuperación
        token = generar_token_verificacion(email)

        # Actualizar usuario con el token
        db.usuarios.update_one(
            {'_id': usuario['_id']},
            {'$set': {'token_recuperacion': token}}
        )

        # Enviar email con el enlace de recuperación
        link_recuperacion = url_for('reset_password', token=token, email=email, _external=True)
        
        cuerpo_email = render_template(
            'emails/reset_password.html',
            nombre_usuario=usuario.get('nombre_usuario', 'Usuario'),
            link_recuperacion=link_recuperacion
        )

        if enviar_email(email, "Cambio de contraseña - CAE Accesible", cuerpo_email):
            flash('Te hemos enviado un email con las instrucciones para cambiar tu contraseña', 'success')
        else:
            flash('Error al enviar el email. Por favor, intenta nuevamente', 'danger')

        return redirect(url_for('usuarios.usuario_actualizar'))

    except Exception as e:
        flash(f'Error al procesar la solicitud: {str(e)}', 'danger')
        return redirect(url_for('usuarios.usuario_actualizar'))
