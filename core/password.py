from flask import render_template, session, redirect, url_for, flash, request
from datetime import datetime
from config import conexion_mongo
from utils.token_utils import verificar_token, generar_token_verificacion
from utils.email_utils import enviar_email

db = conexion_mongo()

def verificar_email_vista():
    # Obtener token y email de la URL o la sesión
    token = request.args.get('token') or session.get('verification_token')
    email = request.args.get('email') or session.get('verification_email')

    if not token or not email:
        flash('No hay una verificación pendiente.', 'danger')
        return redirect(url_for('index'))

    # Guardar token y email en la sesión si vienen de la URL
    if request.args.get('token'):
        session['verification_token'] = token
        session['verification_email'] = email

    if request.method == 'POST':
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        if not password or not password_confirm:
            flash('Por favor, introduce una contraseña', 'danger')
            return render_template('verificar_email.html', email=email)

        if password != password_confirm:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('verificar_email.html', email=email)

        # Verificar que el token sea válido
        if not verificar_token(token):
            flash('El enlace de verificación ha expirado. Por favor, solicita uno nuevo.', 'danger')
            # Limpiar la sesión
            session.pop('verification_token', None)
            session.pop('verification_email', None)
            return redirect(url_for('index'))

        # Actualizar usuario
        resultado = db.usuarios.update_one(
            {'email': email, 'token_verificacion': token},
            {
                '$set': {
                    'password': password,
                    'verificado': True,
                    'estado_usuario': 'activo',
                    'fecha_modificacion': datetime.now(),
                    'token_verificacion': None
                }
            }
        )

        if resultado.modified_count > 0:
            # Limpiar la sesión
            session.pop('verification_token', None)
            session.pop('verification_email', None)
            flash('Tu cuenta ha sido activada correctamente. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        else:
            flash('No se pudo activar la cuenta. Por favor, contacta con soporte.', 'danger')
            return redirect(url_for('index'))

    # GET request
    # Verificar que el token sea válido
    if not verificar_token(token):
        flash('El enlace de verificación ha expirado. Por favor, solicita uno nuevo.', 'danger')
        # Limpiar la sesión
        session.pop('verification_token', None)
        session.pop('verification_email', None)
        return redirect(url_for('index'))

    usuario = db.usuarios.find_one({'email': email, 'token_verificacion': token})
    if not usuario:
        flash('No se encontró el usuario o ya está verificado.', 'danger')
        # Limpiar la sesión
        session.pop('verification_token', None)
        session.pop('verification_email', None)
        return redirect(url_for('index'))

    return render_template('verificar_email.html', email=email)

def recuperar_password_vista():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Por favor, introduce tu email', 'danger')
            return render_template('recuperar_password.html')

        # Verificar si el usuario existe
        usuario = db.usuarios.find_one({'email': email})
        if not usuario:
            flash('No se encontró ninguna cuenta con ese email', 'danger')
            return render_template('recuperar_password.html')

        # Generar token de recuperación
        token = generar_token_verificacion(email)

        # Actualizar usuario con el token
        db.usuarios.update_one(
            {'email': email},
            {'$set': {'token_recuperacion': token}}
        )

        # Enviar email con el enlace de recuperación
        link_recuperacion = url_for('reset_password', token=token, email=email, _external=True)
        cuerpo_email = f"""
        <h2>Recuperación de Contraseña</h2>
        <p>Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace para crear una nueva:</p>
        <p><a href="{link_recuperacion}">Restablecer contraseña</a></p>
        <p>Este enlace expirará en 1 hora.</p>
        <p>Si no solicitaste este cambio, puedes ignorar este correo.</p>
        """

        if enviar_email(email, "Recuperación de contraseña - CAE Accesible", cuerpo_email):
            flash('Te hemos enviado un email con las instrucciones para recuperar tu contraseña', 'success')
            return redirect(url_for('login'))
        else:
            flash('Error al enviar el email. Por favor, intenta nuevamente', 'danger')
            return render_template('recuperar_password.html')

    return render_template('recuperar_password.html')

def reset_password_vista():
    # Obtener token y email de la URL o la sesión
    token = request.args.get('token') or session.get('reset_token')
    email = request.args.get('email') or session.get('reset_email')

    if not token or not email:
        flash('Enlace de recuperación inválido', 'danger')
        return redirect(url_for('login'))

    # Guardar token y email en la sesión si vienen de la URL
    if request.args.get('token'):
        session['reset_token'] = token
        session['reset_email'] = email

    if request.method == 'POST':
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        if not password or not password_confirm:
            flash('Por favor, introduce una contraseña', 'danger')
            return render_template('reset_password.html', email=email)

        if password != password_confirm:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('reset_password.html', email=email)

        # Verificar que el token sea válido
        if not verificar_token(token):
            flash('El enlace de recuperación ha expirado. Por favor, solicita uno nuevo.', 'danger')
            session.pop('reset_token', None)
            session.pop('reset_email', None)
            return redirect(url_for('recuperar_password'))

        # Actualizar contraseña
        resultado = db.usuarios.update_one(
            {'email': email, 'token_recuperacion': token},
            {
                '$set': {
                    'password': password,
                    'fecha_modificacion': datetime.now(),
                    'token_recuperacion': None
                }
            }
        )

        if resultado.modified_count > 0:
            session.pop('reset_token', None)
            session.pop('reset_email', None)
            flash('Tu contraseña ha sido actualizada. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        else:
            flash('No se pudo actualizar la contraseña. Por favor, intenta nuevamente.', 'danger')
            return redirect(url_for('recuperar_password'))

    # GET request
    # Verificar que el token sea válido
    if not verificar_token(token):
        flash('El enlace de recuperación ha expirado. Por favor, solicita uno nuevo.', 'danger')
        session.pop('reset_token', None)
        session.pop('reset_email', None)
        return redirect(url_for('recuperar_password'))

    usuario = db.usuarios.find_one({'email': email, 'token_recuperacion': token})
    if not usuario:
        flash('Enlace de recuperación inválido', 'danger')
        session.pop('reset_token', None)
        session.pop('reset_email', None)
        return redirect(url_for('recuperar_password'))

    return render_template('reset_password.html', email=email)
