from flask import Blueprint

from core.usuarios_cogestores import (
    gestores_usuarios_cogestores_vista,
    gestores_usuarios_cogestores_crear_vista,
    gestores_usuarios_cogestores_actualizar_vista,
    gestores_usuarios_cogestores_eliminar_vista
)

from core._decoradores import login_requerido
usuarios_cogestores_bp = Blueprint('usuarios_cogestores', __name__, url_prefix='/usuarios-cogestores')


@usuarios_cogestores_bp.route('/', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_cogestores():
    return gestores_usuarios_cogestores_vista()

@usuarios_cogestores_bp.route('/crear', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_cogestores_crear():
    return gestores_usuarios_cogestores_crear_vista()

@usuarios_cogestores_bp.route('/actualizar', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_cogestores_actualizar():
    return gestores_usuarios_cogestores_actualizar_vista()

@usuarios_cogestores_bp.route('/eliminar', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_cogestores_eliminar():
    return gestores_usuarios_cogestores_eliminar_vista()










