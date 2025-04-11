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

@ug_usuarios_centros_bp.route('/', methods=['GET', 'POST'])
@login_requerido
def usuarios_centros():
    return usuarios_centros_vista()

@ug_usuarios_centros_bp.route('/crear', methods=['GET', 'POST'])
@login_requerido
def usuarios_centros_crear():
    return usuarios_centros_crear_vista()

@ug_usuarios_centros_bp.route('/actualizar', methods=['GET', 'POST'])
@login_requerido
def usuarios_centros_actualizar():
    return usuarios_centros_actualizar_vista()

@ug_usuarios_centros_bp.route('/eliminar', methods=['GET', 'POST'])
@login_requerido
def usuarios_centros_eliminar():
    return usuarios_centros_eliminar_vista()









