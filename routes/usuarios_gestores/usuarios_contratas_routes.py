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

@ug_usuarios_contratas_bp.route('/', methods=['GET', 'POST'])
@login_requerido
def usuarios_contratas():
    return usuarios_contratas_vista()

@ug_usuarios_contratas_bp.route('/crear', methods=['GET', 'POST'])
@login_requerido
def usuarios_contratas_crear():
    return usuarios_contratas_crear_vista()

@ug_usuarios_contratas_bp.route('/actualizar', methods=['GET', 'POST'])
@login_requerido
def usuarios_contratas_actualizar():
    return usuarios_contratas_actualizar_vista()

@ug_usuarios_contratas_bp.route('/eliminar', methods=['GET', 'POST'])
@login_requerido
def usuarios_contratas_eliminar():
    return usuarios_contratas_eliminar_vista()














