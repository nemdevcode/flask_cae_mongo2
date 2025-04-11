from flask import Blueprint

from core.usuarios_gestores.usuarios_cogestores import (
    usuarios_cogestores_vista,
    usuarios_cogestores_crear_vista,
    usuarios_cogestores_actualizar_vista,
    usuarios_cogestores_eliminar_vista
)

from core._decoradores import login_requerido
ug_usuarios_cogestores_bp = Blueprint('ug_usuarios_cogestores', __name__, url_prefix='/usuarios-gestores/usuarios-cogestores')


@ug_usuarios_cogestores_bp.route('/', methods=['GET', 'POST'])
@login_requerido
def usuarios_cogestores():
    return usuarios_cogestores_vista()

@ug_usuarios_cogestores_bp.route('/crear', methods=['GET', 'POST'])
@login_requerido
def usuarios_cogestores_crear():
    return usuarios_cogestores_crear_vista()

@ug_usuarios_cogestores_bp.route('/actualizar', methods=['GET', 'POST'])
@login_requerido
def usuarios_cogestores_actualizar():
    return usuarios_cogestores_actualizar_vista()

@ug_usuarios_cogestores_bp.route('/eliminar', methods=['GET', 'POST'])
@login_requerido
def usuarios_cogestores_eliminar():
    return usuarios_cogestores_eliminar_vista()










