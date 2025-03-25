from flask import render_template, session, redirect, url_for, flash, request

from routes.centros_routes import centros_bp
from routes.cogestores_routes import cogestores_bp
from routes.gestores_routes import gestores_bp
from routes.titulares_routes import titulares_bp
from routes.usuarios_routes import usuarios_bp

from core.login import login_vista
from core.registrate import registrate_vista
from utils.token_utils import verificar_token
from datetime import datetime
from config import conexion_mongo
from bson import ObjectId

db = conexion_mongo()

def rutas(app):
    """Registra todas las rutas de la aplicación"""
    # Registrar blueprints
    app.register_blueprint(centros_bp)
    app.register_blueprint(cogestores_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(titulares_bp)
    app.register_blueprint(gestores_bp)

    # Rutas comunes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        return login_vista()

    @app.route('/registrate', methods=['GET', 'POST'])
    def registrate():
        return registrate_vista()

    @app.route('/verificar-email', methods=['GET', 'POST'])
    def verificar_email():
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
                        'estado': 'activo',
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

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Has cerrado sesión correctamente.', 'success')
        return redirect(url_for('index'))
    

    

