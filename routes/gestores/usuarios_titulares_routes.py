from flask import Blueprint

from core.usuarios_titulares import (
    gestores_usuarios_titulares_vista,
    gestores_usuarios_titulares_crear_vista,
    gestores_usuarios_titulares_actualizar_vista,
    gestores_usuarios_titulares_eliminar_vista
)

from core._decoradores import login_requerido
usuarios_titulares_bp = Blueprint('usuarios_titulares', __name__, url_prefix='/usuarios-titulares')

'''
Rutas para gestión de usuarios titulares, funciones:
    - gestores_usuarios_titulares_vista()
    - gestores_usuarios_titulares_crear_vista()
    - gestores_usuarios_titulares_actualizar_vista()
    - gestores_usuarios_titulares_eliminar_vista()
'''

@usuarios_titulares_bp.route('/usuarios/usuarios-gestores/usuarios-titulares/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_titulares(titular_id):
    return gestores_usuarios_titulares_vista(titular_id)

@usuarios_titulares_bp.route('/usuarios/usuarios-gestores/usuarios-titulares/crear/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_titulares_crear(gestor_id, titular_id):
    return gestores_usuarios_titulares_crear_vista(gestor_id, titular_id)

@usuarios_titulares_bp.route('/usuarios/usuarios-gestores/usuarios-titulares/actualizar/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_titulares_actualizar(titular_id):
    return gestores_usuarios_titulares_actualizar_vista(titular_id)

@usuarios_titulares_bp.route('/usuarios/usuarios-gestores/usuarios-titulares/eliminar/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_titulares_eliminar(titular_id):
    return gestores_usuarios_titulares_eliminar_vista(titular_id)


