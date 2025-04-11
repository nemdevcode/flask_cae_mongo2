from flask import Blueprint
from core.gestores import (
    gestores_crear_vista,
    gestores_actualizar_vista,
    gestores_eliminar_vista
)
from core.titulares import gestores_titulares_vista

from core._decoradores import login_requerido
gestores_bp = Blueprint('gestores', __name__, url_prefix='/gestores')


@gestores_bp.route('/crear', methods=['GET', 'POST'])
@login_requerido
def gestores_crear():
    return gestores_crear_vista()

@gestores_bp.route('/actualizar/<gestor_id>', methods=['GET', 'POST'])
@login_requerido
def gestores_actualizar(gestor_id):
    return gestores_actualizar_vista(gestor_id)

@gestores_bp.route('/eliminar/<gestor_id>', methods=['GET'])
@login_requerido
def gestores_eliminar(gestor_id):
    return gestores_eliminar_vista(gestor_id)

@gestores_bp.route('/titulares/<gestor_id>', methods=['GET'])
@login_requerido
def gestores_titulares(gestor_id):
    return gestores_titulares_vista(gestor_id) 