from flask import Blueprint

from core.usuarios_cogestores.usuarios_cogestores import (
    usuarios_cogestores_vista,
    usuarios_cogestores_usuario_gestor_vista
)

from core._decoradores import login_requerido

# Crear el Blueprint para las rutas de cogestores
usuarios_cogestores_bp = Blueprint('usuarios_cogestores', __name__, url_prefix='/usuarios-cogestores')

# Rutas para usuarios cogestores
@usuarios_cogestores_bp.route('/', methods=['GET', 'POST'])
@login_requerido
def usuarios_cogestores():
    return usuarios_cogestores_vista()

@usuarios_cogestores_bp.route('/usuario-gestor/<usuario_rol_cogestor_id>/<usuario_rol_gestor_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_cogestores_usuario_gestor(usuario_rol_cogestor_id, usuario_rol_gestor_id):
    return usuarios_cogestores_usuario_gestor_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id) 