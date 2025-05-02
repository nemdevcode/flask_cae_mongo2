from flask import Blueprint
from core.usuarios_cogestores.gestores import (
    gestores_crear_vista,
    gestores_actualizar_vista,
    gestores_eliminar_vista,
    gestor_vista
)
# from core.usuarios_cogestores.titulares import titulares_vista

from core._decoradores import login_requerido
uc_gestores_bp = Blueprint('uc_gestores', __name__, url_prefix='/usuarios-cogestores/gestores')


@uc_gestores_bp.route('/crear/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>', methods=['GET', 'POST'])
@login_requerido
def gestores_crear(usuario_rol_cogestor_id, usuario_rol_gestor_id):
    return gestores_crear_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id)

@uc_gestores_bp.route('/actualizar/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>', methods=['GET', 'POST'])
@login_requerido
def gestores_actualizar(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id):
    return gestores_actualizar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id)

@uc_gestores_bp.route('/eliminar/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>', methods=['GET', 'POST'])
@login_requerido
def gestores_eliminar(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id):
    return gestores_eliminar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id)

@uc_gestores_bp.route('/gestor/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>', methods=['GET'])
@login_requerido
def gestor(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id):
    return gestor_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id)

# @uc_gestores_bp.route('/titulares/<gestor_id>', methods=['GET'])
# @login_requerido
# def gestores_titulares(gestor_id):
#     return titulares_vista(gestor_id) 