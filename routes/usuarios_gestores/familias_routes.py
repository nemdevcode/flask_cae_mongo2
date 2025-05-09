from flask import Blueprint

from core.usuarios_gestores.familias import (
    familias_vista,
    familias_crear_vista,
    familias_actualizar_vista,
    familias_eliminar_vista,
    familias_asignacion_requerimientos_vista
)

from core._decoradores import login_requerido

ug_familias_bp = Blueprint('ug_familias', __name__, url_prefix='/usuarios-gestores/familias')

'''
Rutas para gestión de familias, funciones:
    - familias_vista()
    - familias_crear_vista()
    - familias_actualizar_vista()
    - familias_eliminar_vista()
'''

@ug_familias_bp.route('/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def familias(gestor_id, titular_id):
    return familias_vista(gestor_id, titular_id)

@ug_familias_bp.route('/crear/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def familias_crear(gestor_id, titular_id):
    return familias_crear_vista(gestor_id, titular_id)

@ug_familias_bp.route('/actualizar/<gestor_id>/<titular_id>/<familia_id>', methods=['GET', 'POST'])
@login_requerido
def familias_actualizar(gestor_id, titular_id, familia_id):
    return familias_actualizar_vista(gestor_id, titular_id, familia_id)

@ug_familias_bp.route('/eliminar/<gestor_id>/<titular_id>/<familia_id>', methods=['GET', 'POST'])
@login_requerido
def familias_eliminar(gestor_id, titular_id, familia_id):
    return familias_eliminar_vista(gestor_id, titular_id, familia_id)

@ug_familias_bp.route('/asignacion-requerimientos/<gestor_id>/<titular_id>/<familia_id>', methods=['GET', 'POST'])
@login_requerido
def familias_asignacion_requerimientos(gestor_id, titular_id, familia_id):
    return familias_asignacion_requerimientos_vista(gestor_id, titular_id, familia_id)

