from flask import Blueprint

from core.usuarios_gestores.titulares import (
    titulares_vista,
    titulares_crear_vista,
    titulares_actualizar_vista,
    titulares_eliminar_vista,
    titulares_titular_vista
)

from core._decoradores import login_requerido

ug_titulares_bp = Blueprint('ug_titulares', __name__, url_prefix='/usuarios-gestores/titulares')

'''
Rutas para gestión de titulares, funciones:
    - titulares_vista()
    - titulares_crear_vista()
    - titulares_actualizar_vista()
    - titulares_eliminar_vista()
'''

@ug_titulares_bp.route('/<gestor_id>', methods=['GET', 'POST'])
@login_requerido
def titulares(gestor_id):
    return titulares_vista(gestor_id)

@ug_titulares_bp.route('/crear/<gestor_id>', methods=['GET', 'POST'])
@login_requerido
def titulares_crear(gestor_id):
    return titulares_crear_vista(gestor_id)

@ug_titulares_bp.route('/actualizar/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def titulares_actualizar(gestor_id, titular_id):
    return titulares_actualizar_vista(gestor_id, titular_id)

@ug_titulares_bp.route('/eliminar/<gestor_id>/<titular_id>', methods=['POST'])
@login_requerido
def titulares_eliminar(gestor_id, titular_id):
    return titulares_eliminar_vista(gestor_id, titular_id)

'''
Rutas para gestión de elementos de cada titular, funciones:
    - titulares_titular_vista()
'''

@ug_titulares_bp.route('/titular/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def titulares_titular(gestor_id, titular_id):
    return titulares_titular_vista(gestor_id, titular_id)









