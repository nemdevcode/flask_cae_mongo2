from flask import Blueprint

from core.usuarios_cogestores.centros import (
    centros_vista,
    centros_crear_vista,
    centros_actualizar_vista,
    centros_eliminar_vista,
    centros_centro_vista
)

from core._decoradores import login_requerido
uc_centros_bp = Blueprint('uc_centros', __name__, url_prefix='/usuarios-cogestores/titulares/titular/centros')


'''
Rutas para gestión de centros, funciones:
    - centros_vista()
    - centros_crear_vista()
    - centros_actualizar_vista()
    - centros_eliminar_vista()
'''

@uc_centros_bp.route('/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def centros(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    return centros_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id)

@uc_centros_bp.route('/crear/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def centros_crear(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    return centros_crear_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id)

@uc_centros_bp.route('/actualizar/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>/<centro_id>', methods=['GET', 'POST'])
@login_requerido
def centros_actualizar(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id):
    return centros_actualizar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id)

@uc_centros_bp.route('/eliminar/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>/<centro_id>', methods=['GET', 'POST'])
@login_requerido
def centros_eliminar(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id):
    return centros_eliminar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id)

'''
Rutas para gestión de elementos de cada centro, funciones:
    - centros_centro_vista()
'''

@uc_centros_bp.route('/centro/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>/<gestor_id>/<titular_id>/<centro_id>', methods=['GET', 'POST'])
@login_requerido
def centros_centro(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id):
    return centros_centro_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id)