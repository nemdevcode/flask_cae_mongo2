from flask import Blueprint

from core.contratas import (
    gestores_contratas_vista,
    gestores_contratas_crear_vista,
    gestores_contratas_actualizar_vista,
    gestores_contratas_eliminar_vista
)

from core._decoradores import login_requerido
contratas_bp = Blueprint('contratas', __name__, url_prefix='/contratas')

'''
Rutas para gestión de contratas, funciones:
    - gestores_contratas_vista()
    - gestores_contratas_crear_vista()
    - gestores_contratas_actualizar_vista()
    - gestores_contratas_eliminar_vista()
'''
@contratas_bp.route('/usuarios/usuarios-gestores/contratas', methods=['GET', 'POST'])
@login_requerido
def gestores_contratas():
    return gestores_contratas_vista()

@contratas_bp.route('/usuarios/usuarios-gestores/contratas/crear', methods=['GET', 'POST'])
@login_requerido
def gestores_contratas_crear():
    return gestores_contratas_crear_vista()

@contratas_bp.route('/usuarios/usuarios-gestores/contratas/actualizar', methods=['GET', 'POST'])
@login_requerido
def gestores_contratas_actualizar():
    return gestores_contratas_actualizar_vista()

@contratas_bp.route('/usuarios/usuarios-gestores/contratas/eliminar', methods=['GET', 'POST'])
@login_requerido
def gestores_contratas_eliminar():
    return gestores_contratas_eliminar_vista()