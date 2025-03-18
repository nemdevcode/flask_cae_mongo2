from flask import Blueprint
from core.usuarios_titulares import (
    usuarios_titulares_vista,
    usuarios_titulares_gestor_vista
)
from core._decoradores import login_requerido

# Crear el Blueprint para las rutas de titulares
titulares_bp = Blueprint('titulares', __name__)

# Rutas para usuarios titulares
@titulares_bp.route('/usuarios/titulares', methods=['GET'])
@login_requerido
def usuarios_titulares():
    return usuarios_titulares_vista()

@titulares_bp.route('/usuarios/titulares/gestor', methods=['GET'])
@login_requerido
def usuarios_titulares_gestor():
    return usuarios_titulares_gestor_vista()





