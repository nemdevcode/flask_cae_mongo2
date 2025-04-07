from flask import Blueprint

from core.usuarios_gestores import (
    usuarios_gestores_vista,
    usuarios_gestores_eliminar_vista,
    usuarios_gestores_gestor_vista
)

from core.gestores import (
    gestores_crear_vista,
    gestores_actualizar_vista,
    gestores_eliminar_vista
)

from core.usuarios_cogestores import (
    gestores_usuarios_cogestores_vista,
    gestores_usuarios_cogestores_crear_vista,
    gestores_usuarios_cogestores_actualizar_vista,
    gestores_usuarios_cogestores_eliminar_vista
)
from core.titulares import (
    gestores_titulares_vista,
    gestores_titulares_crear_vista,
    gestores_titulares_actualizar_vista,
    gestores_titulares_eliminar_vista
)

from core.usuarios_titulares import (
    gestores_usuarios_titulares_vista,
    gestores_usuarios_titulares_crear_vista,
    gestores_usuarios_titulares_actualizar_vista,
    gestores_usuarios_titulares_eliminar_vista
)

from core.centros import (
    gestores_centros_vista,
    gestores_centros_crear_vista,
    gestores_centros_actualizar_vista,
    gestores_centros_eliminar_vista
)

from core.usuarios_centros import (
    gestores_usuarios_centros_vista,
    gestores_usuarios_centros_crear_vista,
    gestores_usuarios_centros_actualizar_vista,
    gestores_usuarios_centros_eliminar_vista
)

from core.contratas import (
    gestores_contratas_vista,
    gestores_contratas_crear_vista,
    gestores_contratas_actualizar_vista,
    gestores_contratas_eliminar_vista
)

from core.usuarios_contratas import (
    gestores_usuarios_contratas_vista,
    gestores_usuarios_contratas_crear_vista,
    gestores_usuarios_contratas_actualizar_vista,
    gestores_usuarios_contratas_eliminar_vista
)

from core._decoradores import login_requerido
gestores_bp = Blueprint('gestores', __name__)

'''
Rutas para gestión de usuarios gestores, funciones:
    - usuarios_gestores_vista()
    - usuarios_gestores_eliminar_vista()
'''

@gestores_bp.route('/usuarios/usuarios-gestores', methods=['GET', 'POST'])
@login_requerido
def usuarios_gestores():
    return usuarios_gestores_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/eliminar', methods=['GET', 'POST'])
@login_requerido
def usuarios_gestores_eliminar():
    return usuarios_gestores_eliminar_vista()

'''
Rutas para gestión de usuarios de cada gestor, funciones:
    - usuarios_gestores_gestor_vista()
'''

@gestores_bp.route('/usuarios/usuarios-gestores/gestor/<gestor_id>', methods=['GET', 'POST'])
@login_requerido
def usuarios_gestores_gestor(gestor_id):
    return usuarios_gestores_gestor_vista(gestor_id)

'''
Rutas para gestión de gestores, funciones:
    - gestores_crear_vista()
    - gestores_actualizar_vista()
    - gestores_eliminar_vista()
'''

@gestores_bp.route('/usuarios/gestores/crear', methods=['GET', 'POST'])
@login_requerido
def gestores_crear():
    return gestores_crear_vista()

@gestores_bp.route('/usuarios/gestores/actualizar', methods=['GET', 'POST'])
@login_requerido
def gestores_actualizar():
    return gestores_actualizar_vista()

@gestores_bp.route('/usuarios/gestores/eliminar/<gestor_id>', methods=['GET', 'POST'])
@login_requerido
def gestores_eliminar(gestor_id):
    return gestores_eliminar_vista(gestor_id)

'''
Rutas para gestión de cogestores, funciones:
    - gestores_usuarios_cogestores_vista()
    - gestores_usuarios_cogestores_crear_vista()
    - gestores_usuarios_cogestores_actualizar_vista()
    - gestores_usuarios_cogestores_eliminar_vista()
'''

@gestores_bp.route('/usuarios/gestores/usuarios-cogestores', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_cogestores():
    return gestores_usuarios_cogestores_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/usuarios-cogestores/crear', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_cogestores_crear():
    return gestores_usuarios_cogestores_crear_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/usuarios-cogestores/actualizar', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_cogestores_actualizar():
    return gestores_usuarios_cogestores_actualizar_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/usuarios-cogestores/eliminar', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_cogestores_eliminar():
    return gestores_usuarios_cogestores_eliminar_vista()

'''
Rutas para gestión de titulares, funciones:
    - gestores_titulares_vista()
    - gestores_titulares_crear_vista()
    - gestores_titulares_actualizar_vista()
    - gestores_titulares_eliminar_vista()
'''

@gestores_bp.route('/usuarios/usuarios-gestores/titulares', methods=['GET', 'POST'])
@login_requerido
def gestores_titulares():
    return gestores_titulares_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/titulares/crear', methods=['GET', 'POST'])
@login_requerido
def gestores_titulares_crear():
    return gestores_titulares_crear_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/titulares/actualizar', methods=['GET', 'POST'])
@login_requerido
def gestores_titulares_actualizar():
    return gestores_titulares_actualizar_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/titulares/eliminar', methods=['GET', 'POST'])
@login_requerido
def gestores_titulares_eliminar():
    return gestores_titulares_eliminar_vista()

'''
Rutas para gestión de usuarios titulares, funciones:
    - gestores_usuarios_titulares_vista()
    - gestores_usuarios_titulares_crear_vista()
    - gestores_usuarios_titulares_actualizar_vista()
    - gestores_usuarios_titulares_eliminar_vista()
'''

@gestores_bp.route('/usuarios/usuarios-gestores/usuarios-titulares', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_titulares():
    return gestores_usuarios_titulares_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/usuarios-titulares/crear', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_titulares_crear():
    return gestores_usuarios_titulares_crear_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/usuarios-titulares/actualizar', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_titulares_actualizar():
    return gestores_usuarios_titulares_actualizar_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/usuarios-titulares/eliminar', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_titulares_eliminar():
    return gestores_usuarios_titulares_eliminar_vista()

'''
Rutas para gestión de centros, funciones:
    - gestores_centros_vista()
    - gestores_centros_crear_vista()
    - gestores_centros_actualizar_vista()
    - gestores_centros_eliminar_vista()
'''

@gestores_bp.route('/usuarios/usuarios-gestores/centros', methods=['GET', 'POST'])
@login_requerido
def gestores_centros():
    return gestores_centros_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/centros/crear', methods=['GET', 'POST'])
@login_requerido
def gestores_centros_crear():
    return gestores_centros_crear_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/centros/actualizar', methods=['GET', 'POST'])
@login_requerido
def gestores_centros_actualizar():
    return gestores_centros_actualizar_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/centros/eliminar', methods=['GET', 'POST'])
@login_requerido
def gestores_centros_eliminar():
    return gestores_centros_eliminar_vista()

'''
Rutas para gestión de usuarios en centros, funciones:
    - gestores_usuarios_centros_vista()
    - gestores_usuarios_centros_crear_vista()
    - gestores_usuarios_centros_actualizar_vista()
    - gestores_usuarios_centros_eliminar_vista()
'''

@gestores_bp.route('/usuarios/usuarios-gestores/usuarios-centros', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_centros():
    return gestores_usuarios_centros_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/usuarios-centros/crear', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_centros_crear():
    return gestores_usuarios_centros_crear_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/usuarios-centros/editar', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_centros_actualizar():
    return gestores_usuarios_centros_actualizar_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/usuarios-centros/eliminar', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_centros_eliminar():
    return gestores_usuarios_centros_eliminar_vista()

'''
Rutas para gestión de contratas, funciones:
    - gestores_contratas_vista()
    - gestores_contratas_crear_vista()
    - gestores_contratas_actualizar_vista()
    - gestores_contratas_eliminar_vista()
'''
@gestores_bp.route('/usuarios/usuarios-gestores/contratas', methods=['GET', 'POST'])
@login_requerido
def gestores_contratas():
    return gestores_contratas_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/contratas/crear', methods=['GET', 'POST'])
@login_requerido
def gestores_contratas_crear():
    return gestores_contratas_crear_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/contratas/actualizar', methods=['GET', 'POST'])
@login_requerido
def gestores_contratas_actualizar():
    return gestores_contratas_actualizar_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/contratas/eliminar', methods=['GET', 'POST'])
@login_requerido
def gestores_contratas_eliminar():
    return gestores_contratas_eliminar_vista()

'''
Rutas para gestión de contratas, funciones:
    - gestores_usuarios_contratas_vista()
    - gestores_usuarios_contratas_crear_vista()
    - gestores_usuarios_contratas_actualizar_vista()
    - gestores_usuarios_contratas_eliminar_vista()
'''

@gestores_bp.route('/usuarios/usuarios-gestores/usuarios-contratas', methods=['GET'])
@login_requerido
def gestores_usuarios_contratas():
    return gestores_usuarios_contratas_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/usuarios-contratas/crear', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_contratas_crear():
    return gestores_usuarios_contratas_crear_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/usuarios-contratas/editar', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_contratas_actualizar():
    return gestores_usuarios_contratas_actualizar_vista()

@gestores_bp.route('/usuarios/usuarios-gestores/usuarios-contratas/eliminar', methods=['GET', 'POST'])
@login_requerido
def gestores_usuarios_contratas_eliminar():
    return gestores_usuarios_contratas_eliminar_vista()



