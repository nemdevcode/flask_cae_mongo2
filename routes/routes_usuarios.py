from flask import Blueprint
from core.usuarios import usuarios_vista, actualizar_usuario_vista
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
def actualizar_usuario():
    return actualizar_usuario_vista() 