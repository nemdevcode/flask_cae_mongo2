from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from datetime import datetime
import re

from utils.token_utils import generar_token_verificacion
from utils.email_utils import enviar_email

from config import conexion_mongo

db = conexion_mongo()

def usuarios_vista():
    try:
        # Obtener el ID del usuario actual
        usuario_id = session.get('usuario_id')
        
        if not usuario_id:
            flash('No hay usuario autenticado', 'danger')
            return redirect(url_for('login'))

        # Obtener la información del usuario
        usuario_actual = db.usuarios.find_one({'_id': ObjectId(usuario_id)})
        
        if not usuario_actual:
            flash('Usuario no encontrado', 'danger')
            return redirect(url_for('login'))

        # Obtener los roles del usuario
        usuario_roles = list(db.usuarios_roles.find({'usuario_id': ObjectId(usuario_id)}))

        # Obtener la información completa de los roles
        roles = []
        for usuario_rol in usuario_roles:
            rol = db.roles.find_one({'_id': usuario_rol['rol_id']})
            if rol:
                rol['estado_rol'] = usuario_rol['estado_rol']  # Agregar el estado del rol
                roles.append(rol)

        return render_template('usuarios.html', 
                             usuario_actual=usuario_actual,
                             nombres_roles=roles)

    except Exception as e:
        flash(f'Error al cargar la vista de usuarios: {str(e)}', 'danger')
        return redirect(url_for('login'))
    
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
                'fecha_modificacion': datetime.now()
            }
            
            # Verificar si el email ya existe en otro usuario
            email_existente = db.usuarios.find_one({
                '_id': {'$ne': ObjectId(usuario_id)},  # Excluir el usuario actual
                'email': datos_actualizados['email']
            })
            
            if email_existente:
                usuario = db.usuarios.find_one({'_id': ObjectId(usuario_id)})
                flash('El email ya está registrado por otro usuario', 'danger')
                return render_template('usuarios_actualizar.html', usuario=usuario)
            
            db.usuarios.update_one(
                {'_id': ObjectId(usuario_id)},
                {'$set': datos_actualizados}
            )
            
            flash('Usuario actualizado correctamente', 'success')
            return redirect(url_for('usuarios.usuarios'))
            
        except Exception as e:
            usuario_id = session.get('usuario_id')
            usuario = db.usuarios.find_one({'_id': ObjectId(usuario_id)})
            flash(f'Error al actualizar el usuario: {str(e)}', 'danger')
            return render_template('usuarios_actualizar.html', usuario=usuario)

def usuario_solicitar_cambio_password():
    try:
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            flash('No hay usuario autenticado', 'danger')
            return redirect(url_for('login'))

        # Obtener el email del usuario
        usuario = db.usuarios.find_one({'_id': ObjectId(usuario_id)})
        if not usuario:
            flash('Usuario no encontrado', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        email = usuario['email']

        # Generar token de recuperación
        token = generar_token_verificacion(email)

        # Actualizar usuario con el token
        db.usuarios.update_one(
            {'_id': ObjectId(usuario_id)},
            {'$set': {'token_recuperacion': token}}
        )

        # Enviar email con el enlace de recuperación
        link_recuperacion = url_for('reset_password', token=token, email=email, _external=True)
        cuerpo_email = f"""
        <h2>Cambio de Contraseña</h2>
        <p>Has solicitado cambiar tu contraseña. Haz clic en el siguiente enlace para crear una nueva:</p>
        <p><a href="{link_recuperacion}">Cambiar contraseña</a></p>
        <p>Este enlace expirará en 1 hora.</p>
        <p>Si no solicitaste este cambio, puedes ignorar este correo.</p>
        """

        if enviar_email(email, "Cambio de contraseña - CAE Accesible", cuerpo_email):
            flash('Te hemos enviado un email con las instrucciones para cambiar tu contraseña', 'success')
        else:
            flash('Error al enviar el email. Por favor, intenta nuevamente', 'danger')

        return redirect(url_for('usuarios.usuario_actualizar'))

    except Exception as e:
        flash(f'Error al procesar la solicitud: {str(e)}', 'danger')
        return redirect(url_for('usuarios.usuario_actualizar'))
