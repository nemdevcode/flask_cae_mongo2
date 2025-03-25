from flask import Blueprint
from core.usuarios import (
    usuarios_vista,
    usuario_actualizar_vista,
    usuario_solicitar_cambio_password
)

from core._decoradores import login_requerido

# Crear el Blueprint para las rutas de usuarios
usuarios_bp = Blueprint('usuarios', __name__)

# Rutas para gestión de usuarios
@usuarios_bp.route('/usuarios', methods=['GET', 'POST'])
@login_requerido
def usuarios():
    return usuarios_vista()

@usuarios_bp.route('/usuarios/actualizar', methods=['GET', 'POST'])
@login_requerido
def usuario_actualizar():
    return usuario_actualizar_vista()

@usuarios_bp.route('/usuarios/cambiar-password')
@login_requerido
def solicitar_cambio_password():
    return usuario_solicitar_cambio_password() 