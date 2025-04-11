from flask import Blueprint

from core.titulares import (
    gestores_titulares_vista,
    gestores_titulares_crear_vista,
    gestores_titulares_actualizar_vista,
    gestores_titulares_eliminar_vista,
    gestores_titulares_titular_vista
)

from core._decoradores import login_requerido

titulares_bp = Blueprint('titulares', __name__, url_prefix='/titulares')

'''
Rutas para gestión de titulares, funciones:
    - gestores_titulares_vista()
    - gestores_titulares_crear_vista()
    - gestores_titulares_actualizar_vista()
    - gestores_titulares_eliminar_vista()
'''

@titulares_bp.route('/usuarios/usuarios-gestores/titulares/<gestor_id>', methods=['GET', 'POST'])
@login_requerido
def gestores_titulares(gestor_id):
    return gestores_titulares_vista(gestor_id)

@titulares_bp.route('/usuarios/usuarios-gestores/titulares/crear/<gestor_id>', methods=['GET', 'POST'])
@login_requerido
def gestores_titulares_crear(gestor_id):
    return gestores_titulares_crear_vista(gestor_id)

@titulares_bp.route('/usuarios/usuarios-gestores/titulares/actualizar/<titular_id>/<gestor_id>', methods=['GET', 'POST'])
@login_requerido
def gestores_titulares_actualizar(titular_id, gestor_id):
    return gestores_titulares_actualizar_vista(titular_id, gestor_id)

@titulares_bp.route('/usuarios/usuarios-gestores/titulares/eliminar/<gestor_id>/<titular_id>', methods=['POST'])
@login_requerido
def gestores_titulares_eliminar(gestor_id, titular_id):
    return gestores_titulares_eliminar_vista(titular_id, gestor_id)

'''
Rutas para gestión de elementos de cada titular, funciones:
    - gestores_titulares_titular_vista()
'''

@titulares_bp.route('/usuarios/usuarios-gestores/titulares/titular/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def gestores_titulares_titular(gestor_id, titular_id):
    return gestores_titulares_titular_vista(gestor_id, titular_id)









