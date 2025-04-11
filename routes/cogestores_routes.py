from flask import Blueprint

from core.usuarios_cogestores import (
    usuarios_cogestores_vista,
    usuarios_cogestores_gestor_vista
)

from core._decoradores import login_requerido

# Crear el Blueprint para las rutas de cogestores
cogestores_bp = Blueprint('cogestores', __name__, url_prefix='/usuarios-gestores/usuarios-cogestores')

# Rutas para usuarios cogestores
@cogestores_bp.route('/', methods=['GET', 'POST'])
@login_requerido
def usuarios_cogestores():
    return usuarios_cogestores_vista()

@cogestores_bp.route('/gestor', methods=['GET', 'POST'])
@login_requerido
def usuarios_cogestores_gestor():
    return usuarios_cogestores_gestor_vista() 