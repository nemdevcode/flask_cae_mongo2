from flask import Blueprint

from core.usuarios_contratas.trabajadores import (
    trabajadores_vista,
    trabajadores_crear_vista,
    trabajadores_actualizar_vista,
    trabajadores_asignacion_centros_vista
)

from core._decoradores import login_requerido

# Crear el Blueprint para las rutas de contratas
ucon_trabajadores_bp = Blueprint('ucon_trabajadores', __name__, url_prefix='/usuarios-contratas/trabajadores')

@ucon_trabajadores_bp.route('/<usuario_rol_contrata_id>/<contrata_id>', methods=['GET', 'POST'])
@login_requerido
def trabajadores(usuario_rol_contrata_id, contrata_id):
    return trabajadores_vista(usuario_rol_contrata_id, contrata_id)

@ucon_trabajadores_bp.route('/crear/<usuario_rol_contrata_id>/<contrata_id>', methods=['GET', 'POST'])
@login_requerido
def trabajadores_crear(usuario_rol_contrata_id, contrata_id):
    return trabajadores_crear_vista(usuario_rol_contrata_id, contrata_id)

@ucon_trabajadores_bp.route('/actualizar/<usuario_rol_contrata_id>/<contrata_id>/<trabajador_id>', methods=['GET', 'POST'])
@login_requerido
def trabajadores_actualizar(usuario_rol_contrata_id, contrata_id, trabajador_id):
    return trabajadores_actualizar_vista(usuario_rol_contrata_id, contrata_id, trabajador_id)

@ucon_trabajadores_bp.route('/asignacion-centros/<usuario_rol_contrata_id>/<contrata_id>/<trabajador_id>', methods=['GET', 'POST'])
@login_requerido
def trabajadores_asignacion_centros(usuario_rol_contrata_id, contrata_id, trabajador_id):
    return trabajadores_asignacion_centros_vista(usuario_rol_contrata_id, contrata_id, trabajador_id)
