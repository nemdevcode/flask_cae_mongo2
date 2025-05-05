from flask import Blueprint

from core.usuarios_cogestores.usuarios_titulares import (
    usuarios_titulares_vista,
    usuarios_titulares_crear_vista,
    usuarios_titulares_actualizar_vista,
    usuarios_titulares_eliminar_vista
)

from core._decoradores import login_requerido
uc_usuarios_titulares_bp = Blueprint('uc_usuarios_titulares', __name__, url_prefix='/usuarios-cogestores/usuarios-titulares')

'''
Rutas para gestión de usuarios titulares, funciones:
    - usuarios_titulares_vista()
    - usuarios_titulares_crear_vista()
    - usuarios_titulares_actualizar_vista()
    - usuarios_titulares_eliminar_vista()
'''

@uc_usuarios_titulares_bp.route('/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_titulares(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    return usuarios_titulares_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id)

@uc_usuarios_titulares_bp.route('/crear/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_titulares_crear(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    return usuarios_titulares_crear_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id)

@uc_usuarios_titulares_bp.route('/actualizar/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>/<usuario_titular_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_titulares_actualizar(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, usuario_titular_id):
    return usuarios_titulares_actualizar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, usuario_titular_id)

@uc_usuarios_titulares_bp.route('/eliminar/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>/<usuario_titular_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_titulares_eliminar(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, usuario_titular_id):
    return usuarios_titulares_eliminar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, usuario_titular_id)


