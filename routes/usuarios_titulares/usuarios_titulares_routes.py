from flask import Blueprint

from core.usuarios_titulares.usuarios_titulares import (
    usuarios_titulares_vista,
    usuarios_titulares_gestor_vista
)

from core._decoradores import login_requerido

# Crear el Blueprint para las rutas de cogestores
usuarios_titulares_bp = Blueprint('usuarios_titulares', __name__, url_prefix='/usuarios-titulares')

# Rutas para usuarios cogestores
@usuarios_titulares_bp.route('/<usuario_rol_id>/<usuario_rol_gestor_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_titulares(usuario_rol_id, usuario_rol_gestor_id):
    return usuarios_titulares_vista(usuario_rol_id, usuario_rol_gestor_id)

@usuarios_titulares_bp.route('/gestor/<usuario_rol_id>/<usuario_rol_gestor_id>/<gestor_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_titulares_gestor(usuario_rol_id, usuario_rol_gestor_id, gestor_id):
    return usuarios_titulares_gestor_vista(usuario_rol_id, usuario_rol_gestor_id, gestor_id) 