from flask import Blueprint

from core.usuarios_contratas import (
    gestores_usuarios_contratas_vista,
    gestores_usuarios_contratas_crear_vista,
    gestores_usuarios_contratas_actualizar_vista,
    gestores_usuarios_contratas_eliminar_vista
)

from core._decoradores import login_requerido
usuarios_contratas_bp = Blueprint('usuarios_contratas', __name__, url_prefix='/usuarios-contratas')

'''
Rutas para gestión de usuarios contratas, funciones:
    - gestores_usuarios_contratas_vista()
    - gestores_usuarios_contratas_crear_vista()
    - gestores_usuarios_contratas_actualizar_vista()
    - gestores_usuarios_contratas_eliminar_vista()
'''

@usuarios_contratas_bp.route('/usuarios/usuarios-gestores/usuarios-contratas', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_contratas():
    return gestores_usuarios_contratas_vista()

@usuarios_contratas_bp.route('/usuarios/usuarios-gestores/usuarios-contratas/crear', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_contratas_crear():
    return gestores_usuarios_contratas_crear_vista()

@usuarios_contratas_bp.route('/usuarios/usuarios-gestores/usuarios-contratas/actualizar', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_contratas_actualizar():
    return gestores_usuarios_contratas_actualizar_vista()

@usuarios_contratas_bp.route('/usuarios/usuarios-gestores/usuarios-contratas/eliminar', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_contratas_eliminar():
    return gestores_usuarios_contratas_eliminar_vista()














