from flask import Blueprint
from core.cogestores import (
    usuarios_gestores_cogestores_vista,
    crear_gestores_cogestores_vista,
    actualizar_gestores_cogestores_vista,
    eliminar_gestores_cogestores_vista,
    usuarios_cogestores_vista,
    usuarios_cogestores_gestor_vista
)
from core._decoradores import login_requerido

# Crear el Blueprint para las rutas de cogestores
cogestores_bp = Blueprint('cogestores', __name__)

# Rutas para usuarios cogestores
@cogestores_bp.route('/usuarios/cogestores', methods=['GET'])
@login_requerido
def usuarios_cogestores():
    return usuarios_cogestores_vista()

@cogestores_bp.route('/usuarios/cogestores/gestor', methods=['GET'])
@login_requerido
def usuarios_cogestores_gestor():
    return usuarios_cogestores_gestor_vista() 