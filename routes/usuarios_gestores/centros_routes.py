from flask import Blueprint

from core.usuarios_gestores.centros import (
    centros_vista,
    centros_crear_vista,
    centros_actualizar_vista,
    centros_eliminar_vista
)

from core._decoradores import login_requerido
ug_centros_bp = Blueprint('ug_centros', __name__, url_prefix='/usuarios-gestores/titulares/titular/centros')


'''
Rutas para gestión de centros, funciones:
    - centros_vista()
    - centros_crear_vista()
    - centros_actualizar_vista()
    - centros_eliminar_vista()
'''

@ug_centros_bp.route('/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def centros(gestor_id, titular_id):
    return centros_vista(gestor_id, titular_id)

@ug_centros_bp.route('/crear/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def centros_crear(gestor_id, titular_id):
    return centros_crear_vista(gestor_id, titular_id)

@ug_centros_bp.route('/actualizar/<gestor_id>/<titular_id>/<centro_id>', methods=['GET', 'POST'])
@login_requerido
def centros_actualizar(gestor_id, titular_id, centro_id):
    return centros_actualizar_vista(gestor_id, titular_id, centro_id)

@ug_centros_bp.route('/eliminar/<gestor_id>/<titular_id>/<centro_id>', methods=['GET', 'POST'])
@login_requerido
def centros_eliminar(gestor_id, titular_id, centro_id):
    return centros_eliminar_vista(gestor_id, titular_id, centro_id)