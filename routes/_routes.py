from flask import render_template, session, redirect, url_for, flash, request

from routes.routes_centros import centros_bp
from routes.routes_cogestores import cogestores_bp
from routes.routes_usuarios import usuarios_bp
from routes.routes_titulares import titulares_bp
from routes.routes_gestores import gestores_bp

from core._decoradores import login_requerido

from core.login import login_vista
from core.registrate import registrate_vista

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

    @app.route('/usuarios/titulares')
    @login_requerido
    def titulares():
        return render_template('titulares.html')

    @app.route('/usuarios/gestores/centros')
    @login_requerido
    def gestores_centros():
        return render_template('centros.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Has cerrado sesión correctamente.', 'success')
        return redirect(url_for('index'))
    

    

