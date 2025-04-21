from flask import Blueprint

from core.usuarios_gestores.contratas import (
    contratas_vista,
    contratas_crear_vista,
    contratas_actualizar_vista,
    contratas_eliminar_vista,
    contratas_contrata_vista
)

from core._decoradores import login_requerido
ug_contratas_bp = Blueprint('ug_contratas', __name__, url_prefix='/usuarios-gestores/titulares/titular/contratas')

'''
Rutas para gestión de contratas, funciones:
    - contratas_vista()
    - contratas_crear_vista()
    - contratas_actualizar_vista()
    - contratas_eliminar_vista()
'''
@ug_contratas_bp.route('/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def contratas(gestor_id, titular_id):
    return contratas_vista(gestor_id, titular_id)

@ug_contratas_bp.route('/crear/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def contratas_crear(gestor_id, titular_id):
    return contratas_crear_vista(gestor_id, titular_id)

@ug_contratas_bp.route('/actualizar/<gestor_id>/<titular_id>/<contrata_id>', methods=['GET', 'POST'])
@login_requerido
def contratas_actualizar(gestor_id, titular_id, contrata_id):
    return contratas_actualizar_vista(gestor_id, titular_id, contrata_id)

@ug_contratas_bp.route('/eliminar/<gestor_id>/<titular_id>/<contrata_id>', methods=['GET', 'POST'])
@login_requerido
def contratas_eliminar(gestor_id, titular_id, contrata_id):
    return contratas_eliminar_vista(gestor_id, titular_id, contrata_id)

'''
Rutas para gestión de elementos de cada contratas, funciones:
    - contratas_contrata_vista()
'''

@ug_contratas_bp.route('/contrata/<gestor_id>/<titular_id>/<contrata_id>', methods=['GET', 'POST'])
@login_requerido
def contratas_contrata(gestor_id, titular_id, contrata_id):
    return contratas_contrata_vista(gestor_id, titular_id, contrata_id)
