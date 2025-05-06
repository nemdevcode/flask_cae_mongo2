from flask import Blueprint

from core.usuarios_cogestores.usuarios_contratas import (
    usuarios_contratas_vista,
    usuarios_contratas_crear_vista,
    usuarios_contratas_actualizar_vista,
    usuarios_contratas_eliminar_vista
)

from core._decoradores import login_requerido
uc_usuarios_contratas_bp = Blueprint('uc_usuarios_contratas', __name__, url_prefix='/usuarios-cogestores/usuarios-contratas')

'''
Rutas para gestión de usuarios contratas, funciones:
    - usuarios_contratas_vista()
    - usuarios_contratas_crear_vista()
    - usuarios_contratas_actualizar_vista()
    - usuarios_contratas_eliminar_vista()
'''

@uc_usuarios_contratas_bp.route('/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>/<contrata_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_contratas(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id):
    return usuarios_contratas_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id)

@uc_usuarios_contratas_bp.route('/crear/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>/<contrata_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_contratas_crear(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id):
    return usuarios_contratas_crear_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id)

@uc_usuarios_contratas_bp.route('/actualizar/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>/<contrata_id>/<usuario_contrata_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_contratas_actualizar(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id, usuario_contrata_id):
    return usuarios_contratas_actualizar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id, usuario_contrata_id)

@uc_usuarios_contratas_bp.route('/eliminar/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>/<contrata_id>/<usuario_contrata_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_contratas_eliminar(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id, usuario_contrata_id):
    return usuarios_contratas_eliminar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id, usuario_contrata_id)


