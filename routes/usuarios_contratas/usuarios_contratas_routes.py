from flask import Blueprint

from core.usuarios_contratas.usuarios_contratas import (
    usuarios_contratas_vista,
    usuarios_contratas_contrata_vista
)

from core._decoradores import login_requerido

# Crear el Blueprint para las rutas de contratas
usuarios_contratas_bp = Blueprint('usuarios_contratas', __name__, url_prefix='/usuarios-contratas')

# Rutas para usuarios contratas
@usuarios_contratas_bp.route('/', methods=['GET', 'POST'])
@login_requerido
def usuarios_contratas():
    return usuarios_contratas_vista()

@usuarios_contratas_bp.route('/contrata/<usuario_rol_contrata_id>/<contrata_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_contratas_contrata(usuario_rol_contrata_id, contrata_id):
    return usuarios_contratas_contrata_vista(usuario_rol_contrata_id, contrata_id)


