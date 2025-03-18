from flask import render_template, session, redirect, url_for, flash, request

from routes.centros_routes import centros_bp
from routes.cogestores_routes import cogestores_bp
from routes.gestores_routes import gestores_bp
from routes.titulares_routes import titulares_bp
from routes.usuarios_routes import usuarios_bp

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

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Has cerrado sesión correctamente.', 'success')
        return redirect(url_for('index'))
    

    

