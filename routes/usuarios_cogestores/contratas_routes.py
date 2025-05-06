from flask import Blueprint

from core.usuarios_cogestores.contratas import (
    contratas_vista,
    contratas_crear_vista,
    contratas_actualizar_vista,
    contratas_eliminar_vista,
    contratas_contrata_vista
)

from core._decoradores import login_requerido
uc_contratas_bp = Blueprint('uc_contratas', __name__, url_prefix='/usuarios-cogestores/titulares/titular/contratas')


'''
Rutas para gestión de contratas, funciones:
    - contratas_vista()
    - contratas_crear_vista()
    - contratas_actualizar_vista()
    - contratas_eliminar_vista()
'''

@uc_contratas_bp.route('/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def contratas(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    return contratas_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id)

@uc_contratas_bp.route('/crear/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def contratas_crear(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    return contratas_crear_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id)

@uc_contratas_bp.route('/actualizar/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>/<contrata_id>', methods=['GET', 'POST'])
@login_requerido
def contratas_actualizar(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id):
    return contratas_actualizar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id)

@uc_contratas_bp.route('/eliminar/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>/<contrata_id>', methods=['GET', 'POST'])
@login_requerido
def contratas_eliminar(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id):
    return contratas_eliminar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id)

'''
Rutas para gestión de elementos de cada contrata, funciones:
    - contratas_contrata_vista()
'''

@uc_contratas_bp.route('/contrata/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>/<contrata_id>', methods=['GET', 'POST'])
@login_requerido
def contratas_contrata(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id):
    return contratas_contrata_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id)