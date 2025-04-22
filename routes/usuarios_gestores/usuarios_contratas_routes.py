from flask import Blueprint

from core.usuarios_gestores.usuarios_contratas import (
    usuarios_contratas_vista,
    usuarios_contratas_crear_vista,
    usuarios_contratas_actualizar_vista,
    usuarios_contratas_eliminar_vista
)

from core._decoradores import login_requerido
ug_usuarios_contratas_bp = Blueprint('ug_usuarios_contratas', __name__, url_prefix='/usuarios-gestores/usuarios-contratas')

'''
Rutas para gestión de usuarios contratas, funciones:
    - usuarios_contratas_vista()
    - usuarios_contratas_crear_vista()
    - usuarios_contratas_actualizar_vista()
    - usuarios_contratas_eliminar_vista()
'''

@ug_usuarios_contratas_bp.route('/<gestor_id>/<titular_id>/<contrata_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_contratas(gestor_id, titular_id, contrata_id):
    return usuarios_contratas_vista(gestor_id, titular_id, contrata_id)

@ug_usuarios_contratas_bp.route('/crear/<gestor_id>/<titular_id>/<contrata_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_contratas_crear(gestor_id, titular_id, contrata_id):
    return usuarios_contratas_crear_vista(gestor_id, titular_id, contrata_id)

@ug_usuarios_contratas_bp.route('/actualizar/<gestor_id>/<titular_id>/<contrata_id>/<usuario_contrata_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_contratas_actualizar(gestor_id, titular_id, contrata_id, usuario_contrata_id):
    return usuarios_contratas_actualizar_vista(gestor_id, titular_id, contrata_id, usuario_contrata_id)

@ug_usuarios_contratas_bp.route('/eliminar/<gestor_id>/<titular_id>/<contrata_id>/<usuario_contrata_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_contratas_eliminar(gestor_id, titular_id, contrata_id, usuario_contrata_id):
    return usuarios_contratas_eliminar_vista(gestor_id, titular_id, contrata_id, usuario_contrata_id)
