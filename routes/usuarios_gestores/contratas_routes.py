from flask import Blueprint

from core.usuarios_gestores.contratas import (
    contratas_vista,
    contratas_crear_vista,
    contratas_actualizar_vista,
    contratas_eliminar_vista
)

from core._decoradores import login_requerido
ug_contratas_bp = Blueprint('ug_contratas', __name__, url_prefix='/usuarios-gestores/contratas')

'''
Rutas para gestión de contratas, funciones:
    - contratas_vista()
    - contratas_crear_vista()
    - contratas_actualizar_vista()
    - contratas_eliminar_vista()
'''
@ug_contratas_bp.route('/', methods=['GET', 'POST'])
@login_requerido
def contratas():
    return contratas_vista()

@ug_contratas_bp.route('/crear', methods=['GET', 'POST'])
@login_requerido
def contratas_crear():
    return contratas_crear_vista()

@ug_contratas_bp.route('/actualizar', methods=['GET', 'POST'])
@login_requerido
def contratas_actualizar():
    return contratas_actualizar_vista()

@ug_contratas_bp.route('/eliminar', methods=['GET', 'POST'])
@login_requerido
def contratas_eliminar():
    return contratas_eliminar_vista()