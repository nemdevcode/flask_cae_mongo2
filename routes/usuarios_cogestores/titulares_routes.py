from flask import Blueprint

from core.usuarios_cogestores.titulares import (
    titulares_vista,
    titulares_crear_vista,
    titulares_actualizar_vista,
    titulares_eliminar_vista,
    titulares_titular_vista
)

from core._decoradores import login_requerido

uc_titulares_bp = Blueprint('uc_titulares', __name__, url_prefix='/usuarios-cogestores/titulares')

'''
Rutas para gestión de titulares, funciones:
    - titulares_vista()
    - titulares_crear_vista()
    - titulares_actualizar_vista()
    - titulares_eliminar_vista()
'''

@uc_titulares_bp.route('/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>', methods=['GET', 'POST'])
@login_requerido
def titulares(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id):
    return titulares_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id)

@uc_titulares_bp.route('/crear/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>', methods=['GET', 'POST'])
@login_requerido
def titulares_crear(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id):
    return titulares_crear_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id)

@uc_titulares_bp.route('/actualizar/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def titulares_actualizar(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    return titulares_actualizar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id)

@uc_titulares_bp.route('/eliminar/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>', methods=['POST'])
@login_requerido
def titulares_eliminar(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    return titulares_eliminar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id)

'''
Rutas para gestión de elementos de cada titular, funciones:
    - titulares_titular_vista()
'''

@uc_titulares_bp.route('/titular/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def titulares_titular(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    print(f'ruta usuario_rol_cogestor_id: {usuario_rol_cogestor_id}')
    print(f'ruta usuario_rol_gestor_id: {usuario_rol_gestor_id}')
    print(f'ruta gestor_id: {gestor_id}')
    print(f'ruta titular_id: {titular_id}')
    return titulares_titular_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id)









