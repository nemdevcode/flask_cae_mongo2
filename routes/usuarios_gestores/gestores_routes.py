from flask import Blueprint
from core.usuarios_gestores.gestores import (
    gestores_crear_vista,
    gestores_actualizar_vista,
    gestores_eliminar_vista
)
from core.usuarios_gestores.titulares import titulares_vista

from core._decoradores import login_requerido
ug_gestores_bp = Blueprint('ug_gestores', __name__, url_prefix='/usuarios-gestores/gestores')


@ug_gestores_bp.route('/crear', methods=['GET', 'POST'])
@login_requerido
def gestores_crear():
    return gestores_crear_vista()

@ug_gestores_bp.route('/actualizar/<gestor_id>', methods=['GET', 'POST'])
@login_requerido
def gestores_actualizar(gestor_id):
    return gestores_actualizar_vista(gestor_id)

@ug_gestores_bp.route('/eliminar/<gestor_id>', methods=['GET', 'POST'])
@login_requerido
def gestores_eliminar(gestor_id):
    return gestores_eliminar_vista(gestor_id)

@ug_gestores_bp.route('/titulares/<gestor_id>', methods=['GET'])
@login_requerido
def gestores_titulares(gestor_id):
    return titulares_vista(gestor_id) 