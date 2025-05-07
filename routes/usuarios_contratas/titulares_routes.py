from flask import Blueprint

from core.usuarios_contratas.titulares import (
    titulares_vista,
    titulares_titular_vista
)

from core._decoradores import login_requerido

ucon_titulares_bp = Blueprint('ucon_titulares', __name__, url_prefix='/usuarios-contratas/titulares')

'''
Rutas para gestión de titulares, funciones:
    - titulares_vista()
'''

@ucon_titulares_bp.route('/<usuario_rol_contrata_id>/<contrata_id>', methods=['GET', 'POST'])
@login_requerido
def titulares(usuario_rol_contrata_id, contrata_id):
    return titulares_vista(usuario_rol_contrata_id, contrata_id)

'''
Rutas para gestión de elementos de cada titular, funciones:
    - titulares_titular_vista()
'''

@ucon_titulares_bp.route('/titular/<usuario_rol_contrata_id>/<contrata_id>/<titular_id>', methods=['GET', 'POST'])
@login_requerido
def titulares_titular(usuario_rol_contrata_id, contrata_id, titular_id):
    return titulares_titular_vista(usuario_rol_contrata_id, contrata_id, titular_id)