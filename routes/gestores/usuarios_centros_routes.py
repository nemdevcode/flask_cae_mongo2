from flask import Blueprint

from core.usuarios_centros import (
    gestores_usuarios_centros_vista,
    gestores_usuarios_centros_crear_vista,
    gestores_usuarios_centros_actualizar_vista,
    gestores_usuarios_centros_eliminar_vista
)

from core._decoradores import login_requerido
usuarios_centros_bp = Blueprint('usuarios_centros', __name__, url_prefix='/usuarios-centros')


'''
Rutas para gestión de usuarios centros, funciones:
    - gestores_usuarios_centros_vista()
    - gestores_usuarios_centros_crear_vista()
    - gestores_usuarios_centros_actualizar_vista()
    - gestores_usuarios_centros_eliminar_vista()
'''

@usuarios_centros_bp.route('/usuarios/usuarios-gestores/usuarios-centros', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_centros():
    return gestores_usuarios_centros_vista()

@usuarios_centros_bp.route('/usuarios/usuarios-gestores/usuarios-centros/crear', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_centros_crear():
    return gestores_usuarios_centros_crear_vista()

@usuarios_centros_bp.route('/usuarios/usuarios-gestores/usuarios-centros/actualizar', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_centros_actualizar():
    return gestores_usuarios_centros_actualizar_vista()

@usuarios_centros_bp.route('/usuarios/usuarios-gestores/usuarios-centros/eliminar', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_centros_eliminar():
    return gestores_usuarios_centros_eliminar_vista()









