from flask import Blueprint

from core.usuarios_gestores.requerimientos import (
    requerimientos_vista,
    requerimientos_crear_vista,
    requerimientos_actualizar_vista,
    requerimientos_eliminar_vista
)

from core._decoradores import login_requerido

ug_requerimientos_bp = Blueprint('ug_requerimientos', __name__, url_prefix='/usuarios-gestores/requerimientos')

'''
Rutas para gestión de requerimientos, funciones:
    - requerimientos_vista()
    - requerimientos_crear_vista()
    - requerimientos_actualizar_vista()
    - requerimientos_eliminar_vista()
'''

@ug_requerimientos_bp.route('/<gestor_id>', methods=['GET', 'POST'])
@login_requerido
def requerimientos(gestor_id):
    return requerimientos_vista(gestor_id)

@ug_requerimientos_bp.route('/crear/<gestor_id>', methods=['GET', 'POST'])
@login_requerido
def requerimientos_crear(gestor_id):
    return requerimientos_crear_vista(gestor_id)

@ug_requerimientos_bp.route('/actualizar/<gestor_id>/<requerimiento_id>', methods=['GET', 'POST'])
@login_requerido
def requerimientos_actualizar(gestor_id, requerimiento_id):
    return requerimientos_actualizar_vista(gestor_id, requerimiento_id)

@ug_requerimientos_bp.route('/eliminar/<gestor_id>/<requerimiento_id>', methods=['GET', 'POST'])
@login_requerido
def requerimientos_eliminar(gestor_id, requerimiento_id):
    return requerimientos_eliminar_vista(gestor_id, requerimiento_id)
