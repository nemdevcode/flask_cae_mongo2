from flask import Blueprint
from core.usuarios_gestores import (
    usuarios_gestores_vista,
    usuarios_gestores_eliminar_vista,
    usuarios_gestores_gestor_vista
)

from core._decoradores import login_requerido
usuarios_gestores_bp = Blueprint('usuarios_gestores', __name__, url_prefix='/usuarios-gestores')

# Definir las rutas
@usuarios_gestores_bp.route('/', methods=['GET', 'POST'])
@login_requerido
def usuarios_gestores():
    return usuarios_gestores_vista()

@usuarios_gestores_bp.route('/gestor/<gestor_id>', methods=['GET'])
@login_requerido
def usuarios_gestores_gestor(gestor_id):
    return usuarios_gestores_gestor_vista(gestor_id)

@usuarios_gestores_bp.route('/eliminar/<gestor_id>', methods=['GET'])
@login_requerido
def usuarios_gestores_eliminar(gestor_id):
    return usuarios_gestores_eliminar_vista(gestor_id) 