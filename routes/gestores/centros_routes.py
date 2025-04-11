from flask import Blueprint

from core.centros import (
    gestores_centros_vista,
    gestores_centros_crear_vista,
    gestores_centros_actualizar_vista,
    gestores_centros_eliminar_vista
)

from core._decoradores import login_requerido
centros_bp = Blueprint('centros', __name__, url_prefix='/centros')


'''
Rutas para gestión de centros, funciones:
    - gestores_centros_vista()
    - gestores_centros_crear_vista()
    - gestores_centros_actualizar_vista()
    - gestores_centros_eliminar_vista()
'''

@centros_bp.route('/usuarios/usuarios-gestores/centros', methods=['GET', 'POST'])
@login_requerido
def gestores_centros():
    return gestores_centros_vista()

@centros_bp.route('/usuarios/usuarios-gestores/centros/crear', methods=['GET', 'POST'])
@login_requerido
def gestores_centros_crear():
    return gestores_centros_crear_vista()

@centros_bp.route('/usuarios/usuarios-gestores/centros/actualizar', methods=['GET', 'POST'])
@login_requerido
def gestores_centros_actualizar():
    return gestores_centros_actualizar_vista()

@centros_bp.route('/usuarios/usuarios-gestores/centros/eliminar', methods=['GET', 'POST'])
@login_requerido
def gestores_centros_eliminar():
    return gestores_centros_eliminar_vista()