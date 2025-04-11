from flask import Blueprint

from core.usuarios_gestores.usuarios_titulares import (
    usuarios_titulares_vista,
    usuarios_titulares_crear_vista,
    usuarios_titulares_actualizar_vista,
    usuarios_titulares_eliminar_vista
)

from core._decoradores import login_requerido
ug_usuarios_titulares_bp = Blueprint('ug_usuarios_titulares', __name__, url_prefix='/usuarios-gestores/usuarios-titulares')

'''
Rutas para gestión de usuarios titulares, funciones:
    - usuarios_titulares_vista()
    - usuarios_titulares_crear_vista()
    - usuarios_titulares_actualizar_vista()
    - usuarios_titulares_eliminar_vista()
'''

@ug_usuarios_titulares_bp.route('/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_titulares(titular_id):
    return usuarios_titulares_vista(titular_id)

@ug_usuarios_titulares_bp.route('/crear/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_titulares_crear(gestor_id, titular_id):
    return usuarios_titulares_crear_vista(gestor_id, titular_id)

@ug_usuarios_titulares_bp.route('/actualizar/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_titulares_actualizar(titular_id):
    return usuarios_titulares_actualizar_vista(titular_id)

@ug_usuarios_titulares_bp.route('/eliminar/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_titulares_eliminar(titular_id):
    return usuarios_titulares_eliminar_vista(titular_id)


