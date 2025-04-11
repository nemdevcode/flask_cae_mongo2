from flask import Blueprint

from core.usuarios_gestores.centros import (
    centros_vista,
    centros_crear_vista,
    centros_actualizar_vista,
    centros_eliminar_vista
)

from core._decoradores import login_requerido
ug_centros_bp = Blueprint('ug_centros', __name__, url_prefix='/usuarios-gestores/centros')


'''
Rutas para gestión de centros, funciones:
    - centros_vista()
    - centros_crear_vista()
    - centros_actualizar_vista()
    - centros_eliminar_vista()
'''

@ug_centros_bp.route('/', methods=['GET', 'POST'])
@login_requerido
def centros():
    return centros_vista()

@ug_centros_bp.route('/crear', methods=['GET', 'POST'])
@login_requerido
def centros_crear():
    return centros_crear_vista()

@ug_centros_bp.route('/actualizar', methods=['GET', 'POST'])
@login_requerido
def centros_actualizar():
    return centros_actualizar_vista()

@ug_centros_bp.route('/eliminar', methods=['GET', 'POST'])
@login_requerido
def centros_eliminar():
    return centros_eliminar_vista()