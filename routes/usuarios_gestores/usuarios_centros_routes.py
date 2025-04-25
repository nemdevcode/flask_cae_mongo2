from flask import Blueprint

from core.usuarios_gestores.usuarios_centros import (
    usuarios_centros_vista,
    usuarios_centros_crear_vista,
    usuarios_centros_actualizar_vista,
    usuarios_centros_eliminar_vista
)

from core._decoradores import login_requerido
ug_usuarios_centros_bp = Blueprint('ug_usuarios_centros', __name__, url_prefix='/usuarios-gestores/usuarios-centros')


'''
Rutas para gestión de usuarios centros, funciones:
    - usuarios_centros_vista()
    - usuarios_centros_crear_vista()
    - usuarios_centros_actualizar_vista()
    - usuarios_centros_eliminar_vista()
'''

@ug_usuarios_centros_bp.route('/<gestor_id>/<titular_id>/<centro_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_centros(gestor_id, titular_id, centro_id):
    return usuarios_centros_vista(gestor_id, titular_id, centro_id)

@ug_usuarios_centros_bp.route('/crear/<gestor_id>/<titular_id>/<centro_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_centros_crear(gestor_id, titular_id, centro_id):
    return usuarios_centros_crear_vista(gestor_id, titular_id, centro_id)

@ug_usuarios_centros_bp.route('/actualizar/<gestor_id>/<titular_id>/<centro_id>/<usuario_centro_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_centros_actualizar(gestor_id, titular_id, centro_id, usuario_centro_id):
    return usuarios_centros_actualizar_vista(gestor_id, titular_id, centro_id, usuario_centro_id)

@ug_usuarios_centros_bp.route('/eliminar/<gestor_id>/<titular_id>/<centro_id>/<usuario_centro_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_centros_eliminar(gestor_id, titular_id, centro_id, usuario_centro_id):
    return usuarios_centros_eliminar_vista(gestor_id, titular_id, centro_id, usuario_centro_id)









