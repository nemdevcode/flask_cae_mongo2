import os
from flask import render_template, session, redirect, url_for, flash, request, send_from_directory

from routes.usuarios_routes import usuarios_bp
from routes.usuarios_gestores.usuarios_gestores_routes import usuarios_gestores_bp
from routes.usuarios_gestores.centros_routes import ug_centros_bp
from routes.usuarios_gestores.contratas_routes import ug_contratas_bp
from routes.usuarios_gestores.gestores_routes import ug_gestores_bp
from routes.usuarios_gestores.titulares_routes import ug_titulares_bp
from routes.usuarios_gestores.usuarios_centros_routes import ug_usuarios_centros_bp
from routes.usuarios_gestores.usuarios_contratas_routes import ug_usuarios_contratas_bp
from routes.usuarios_gestores.usuarios_cogestores_routes import ug_usuarios_cogestores_bp
from routes.usuarios_gestores.usuarios_titulares_routes import ug_usuarios_titulares_bp
from routes.usuarios_cogestores.usuarios_cogestores_routes import usuarios_cogestores_bp
from routes.usuarios_cogestores.gestores_routes import uc_gestores_bp
from routes.usuarios_cogestores.titulares_routes import uc_titulares_bp
from routes.usuarios_cogestores.usuarios_titulares_routes import uc_usuarios_titulares_bp
from routes.usuarios_cogestores.centros_routes import uc_centros_bp

from core.login import login_vista
from core.registrate import registrate_vista
from core.password import verificar_email_vista, recuperar_password_vista, reset_password_vista

def rutas(app):
    """Registra todas las rutas de la aplicación"""
    # Registrar blueprints
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(usuarios_gestores_bp)
    app.register_blueprint(ug_centros_bp)
    app.register_blueprint(ug_contratas_bp)
    app.register_blueprint(ug_gestores_bp)
    app.register_blueprint(ug_titulares_bp)
    app.register_blueprint(ug_usuarios_centros_bp)
    app.register_blueprint(ug_usuarios_cogestores_bp)
    app.register_blueprint(ug_usuarios_contratas_bp)
    app.register_blueprint(ug_usuarios_titulares_bp)
    app.register_blueprint(usuarios_cogestores_bp)
    app.register_blueprint(uc_gestores_bp)
    app.register_blueprint(uc_titulares_bp)
    app.register_blueprint(uc_usuarios_titulares_bp)
    app.register_blueprint(uc_centros_bp)

    # Rutas comunes

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')
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
        return verificar_email_vista()

    @app.route('/recuperar-password', methods=['GET', 'POST'])
    def recuperar_password():
        return recuperar_password_vista()

    @app.route('/reset-password', methods=['GET', 'POST'])
    def reset_password():
        return reset_password_vista()

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Has cerrado sesión correctamente.', 'success')
        return redirect(url_for('index'))