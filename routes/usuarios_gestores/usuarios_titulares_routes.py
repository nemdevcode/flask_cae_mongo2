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

@ug_usuarios_titulares_bp.route('/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_titulares(gestor_id, titular_id):
    return usuarios_titulares_vista(gestor_id, titular_id)

@ug_usuarios_titulares_bp.route('/crear/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_titulares_crear(gestor_id, titular_id):
    return usuarios_titulares_crear_vista(gestor_id, titular_id)

@ug_usuarios_titulares_bp.route('/actualizar/<gestor_id>/<titular_id>/<usuario_titular_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_titulares_actualizar(gestor_id, titular_id, usuario_titular_id):
    return usuarios_titulares_actualizar_vista(gestor_id, titular_id, usuario_titular_id)

@ug_usuarios_titulares_bp.route('/eliminar/<gestor_id>/<titular_id>/<usuario_titular_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_titulares_eliminar(gestor_id, titular_id, usuario_titular_id):
    return usuarios_titulares_eliminar_vista(gestor_id, titular_id, usuario_titular_id)


