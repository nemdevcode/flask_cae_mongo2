from flask import Blueprint
from core.gestores import (gestores_vista, 
                           gestores_usuarios_cogestores_vista, 
                           crear_gestores_usuarios_cogestores_vista,
                           actualizar_gestores_usuarios_cogestores_vista, 
                           eliminar_gestores_usuarios_cogestores_vista,
                           gestores_usuarios_titulares_vista, 
                           crear_gestores_usuarios_titulares_vista, 
                           actualizar_gestores_usuarios_titulares_vista,
                           eliminar_gestores_usuarios_titulares_vista, 
                           gestores_centros_vista,
                           crear_gestores_centros_vista,
                           actualizar_gestores_centros_vista,
                           eliminar_gestores_centros_vista,
                           gestores_usuarios_centros_vista, 
                           crear_gestores_usuarios_centros_vista,
                           actualizar_gestores_usuarios_centros_vista,
                           eliminar_gestores_usuarios_centros_vista)

from core._decoradores import login_requerido
gestores_bp = Blueprint('gestores', __name__)

@gestores_bp.route('/usuarios/gestores', methods=['GET'])
@login_requerido
def gestores():
    return gestores_vista()

# Rutas para gestión de cogestores
@gestores_bp.route('/usuarios/gestores/usuarios-cogestores', methods=['GET'])
@login_requerido
def gestores_usuarios_cogestores():
    return gestores_usuarios_cogestores_vista()

@gestores_bp.route('/usuarios/gestores/usuarios-cogestores/crear', methods=['POST'])
@login_requerido
def crear_gestores_usuarios_cogestores():
    return crear_gestores_usuarios_cogestores_vista()

@gestores_bp.route('/usuarios/gestores/usuarios-cogestores/actualizar', methods=['POST'])
@login_requerido
def actualizar_gestores_usuarios_cogestores():
    return actualizar_gestores_usuarios_cogestores_vista()

@gestores_bp.route('/usuarios/gestores/usuarios-cogestores/eliminar', methods=['POST'])
@login_requerido
def eliminar_gestores_usuarios_cogestores():
    return eliminar_gestores_usuarios_cogestores_vista()

# Rutas para gestión de titulares
@gestores_bp.route('/usuarios/gestores/usuarios-titulares', methods=['GET'])
@login_requerido
def gestores_usuarios_titulares():
    return gestores_usuarios_titulares_vista()

@gestores_bp.route('/usuarios/gestores/usuarios-titulares/crear', methods=['POST'])
@login_requerido
def crear_gestores_usuarios_titulares():
    return crear_gestores_usuarios_titulares_vista()

@gestores_bp.route('/usuarios/gestores/usuarios-titulares/actualizar', methods=['POST'])
@login_requerido
def actualizar_gestores_usuarios_titulares():
    return actualizar_gestores_usuarios_titulares_vista()

@gestores_bp.route('/usuarios/gestores/usuarios-titulares/eliminar', methods=['POST'])
@login_requerido
def eliminar_gestores_usuarios_titulares():
    return eliminar_gestores_usuarios_titulares_vista()

'''
Rutas para gestión de centros, funciones:
    - gestores_centros_vista()
    - crear_gestores_centros_vista()
    - actualizar_gestores_centros_vista()
    - eliminar_gestores_centros_vista()
'''

@gestores_bp.route('/usuarios/gestores/centros', methods=['GET'])
@login_requerido
def gestores_centros():
    return gestores_centros_vista()

@gestores_bp.route('/usuarios/gestores/centros/crear', methods=['POST'])
@login_requerido
def crear_gestores_centros():
    return crear_gestores_centros_vista()

@gestores_bp.route('/usuarios/gestores/centros/actualizar', methods=['POST'])
@login_requerido
def actualizar_gestores_centros():
    return actualizar_gestores_centros_vista()

@gestores_bp.route('/usuarios/gestores/centros/eliminar', methods=['POST'])
@login_requerido
def eliminar_gestores_centros():
    return eliminar_gestores_centros_vista()


'''
Rutas para gestión de usuarios en centros, funciones:
    - gestores_usuarios_centros_vista()
    - crear_gestores_usuarios_centros_vista()
    - actualizar_gestores_usuarios_centros_vista()
    - eliminar_gestores_usuarios_centros_vista()
'''

@gestores_bp.route('/usuarios/gestores/usuarios-centros', methods=['GET'])
@login_requerido
def gestores_usuarios_centros():
    return gestores_usuarios_centros_vista()

@gestores_bp.route('/usuarios/gestores/usuarios-centros/crear', methods=['POST'])
@login_requerido
def crear_gestores_usuarios_centros():
    return crear_gestores_usuarios_centros_vista()

@gestores_bp.route('/usuarios/gestores/usuarios-centros/editar', methods=['POST'])
@login_requerido
def actualizar_gestores_usuarios_centros():
    return actualizar_gestores_usuarios_centros_vista()

@gestores_bp.route('/usuarios/gestores/usuarios-centros/eliminar', methods=['POST'])
@login_requerido
def eliminar_gestores_usuarios_centros():
    return eliminar_gestores_usuarios_centros_vista()


