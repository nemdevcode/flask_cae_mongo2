from flask import Blueprint

from core.usuarios_cogestores.usuarios_centros import (
    usuarios_centros_vista,
    usuarios_centros_crear_vista,
    usuarios_centros_actualizar_vista,
    usuarios_centros_eliminar_vista
)

from core._decoradores import login_requerido
uc_usuarios_centros_bp = Blueprint('uc_usuarios_centros', __name__, url_prefix='/usuarios-cogestores/usuarios-centros')

'''
Rutas para gestión de usuarios centros, funciones:
    - usuarios_centros_vista()
    - usuarios_centros_crear_vista()
    - usuarios_centros_actualizar_vista()
    - usuarios_centros_eliminar_vista()
'''

@uc_usuarios_centros_bp.route('/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>/<centro_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_centros(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id):
    return usuarios_centros_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id)

@uc_usuarios_centros_bp.route('/crear/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>/<centro_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_centros_crear(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id):
    return usuarios_centros_crear_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id)

@uc_usuarios_centros_bp.route('/actualizar/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>/<centro_id>/<usuario_centro_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_centros_actualizar(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id, usuario_centro_id):
    return usuarios_centros_actualizar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id, usuario_centro_id)

@uc_usuarios_centros_bp.route('/eliminar/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>/<centro_id>/<usuario_centro_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_centros_eliminar(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id, usuario_centro_id):
    return usuarios_centros_eliminar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id, usuario_centro_id)


