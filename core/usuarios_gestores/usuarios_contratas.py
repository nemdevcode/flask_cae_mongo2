from flask import render_template, request, redirect, url_for, session, flash
from bson import ObjectId
from datetime import datetime
from utils.usuario_utils import (
    crear_usuario,
    verificar_usuario_existente,
    obtener_usuario_autenticado
)
from utils.rol_utils import (
    obtener_rol, 
    crear_rol,
    verificar_rol_gestor
)
from utils.usuario_rol_utils import (
    obtener_usuario_rol, 
    crear_usuario_rol
)
from utils.gestor_utils import obtener_gestor_por_usuario
from utils.titular_utils import obtener_titular_por_id
from utils.usuario_contrata_utils import crear_usuario_contrata
from utils.contrata_utils import obtener_contrata_por_id
from utils.token_utils import generar_token_verificacion
from utils.email_utils import enviar_email
from config import conexion_mongo

db = conexion_mongo()

def verificaciones_consultas(gestor_id, titular_id, contrata_id):
    '''
    Función auxiliar para verificar permisos de gestor y obtener información necesaria
    Retorna:
        - (False, respuesta_redireccion) si hay algún error
        - (True, (usuario, usuario_rol_id, gestor, titular)) si todo está correcto
    '''
    # Obtener usuario autenticado y verificar permisos
    usuario, respuesta_redireccion = obtener_usuario_autenticado()
    if respuesta_redireccion:
        return False, respuesta_redireccion

    # Verificar rol de gestor
    tiene_rol, usuario_rol_id = verificar_rol_gestor(usuario['_id'])
    if not tiene_rol:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return False, redirect(url_for('usuarios.usuarios'))

    # Obtener el gestor asociado al usuario_rol_id
    gestor = obtener_gestor_por_usuario(gestor_id, usuario_rol_id)
    if not gestor:
        flash('Gestor no encontrado o no tienes permisos para acceder', 'danger')
        return False, redirect(url_for('usuarios_gestores.usuarios_gestores_gestor', gestor_id=gestor_id))

    # Obtener la información del titular
    titular = obtener_titular_por_id(titular_id)
    if not titular:
        flash('Titular no encontrado', 'danger')
        return False, redirect(url_for('ug_titulares.titulares_titular', gestor_id=gestor_id, titular_id=titular_id))
    
    # Obtener la información de la contrata
    contrata = obtener_contrata_por_id(contrata_id)
    if not contrata:
        flash('Contrata no encontrada', 'danger')
        return False, redirect(url_for('ug_contratas.contratas_contrata', gestor_id=gestor_id, titular_id=titular_id, contrata_id=contrata_id))

    return True, (usuario, usuario_rol_id, gestor, titular, contrata)

def usuarios_contratas_vista(gestor_id, titular_id, contrata_id):
    print(gestor_id, titular_id, contrata_id)
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id, contrata_id)
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_id, gestor, titular = resultado
        nombre_gestor = gestor.get('nombre_gestor', 'Gestor')

        # Obtener parámetros de filtrado
        filtrar_contrata = request.form.get('filtrar_contrata', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('ug_usuarios_titulares.usuarios_titulares', gestor_id=gestor_id, titular_id=titular_id))
        
        # Construir la consulta base - buscar usuarios contratas donde el titular_id sea el del titular actual
        query = {'titular_id': ObjectId(titular_id)}
        
        # Aplicar filtros si existen
        if filtrar_contrata:
            query['alias_usuario_contrata'] = {'$regex': filtrar_contrata, '$options': 'i'}

        if filtrar_estado != 'todos':
            query['estado_usuario_contrata'] = filtrar_estado
        

        # Obtener los usuarios contratas asociados al titular_id
        usuarios_contratas = []
        usuarios_contratas_cursor = db.usuarios_contratas.find(query)
        
        # Obtener el rol de titular
        existe_rol, rol_titular_id = obtener_rol('titular')
        if not existe_rol:
            flash('Rol de titular no encontrado', 'danger')
            return redirect(url_for('ug_titulares.titulares_titular', gestor_id=gestor_id, titular_id=titular_id))
        
        for uc in usuarios_contratas_cursor:
            # Obtener el usuario_rol del titular usando la función obtener_usuario_rol
            usuario_rol = db.usuarios_roles.find_one({'_id': uc['usuario_rol_contrata_id']})
            
            if usuario_rol:
                # Obtener la información del usuario titular
                usuario_contrata = db.usuarios.find_one({'_id': ObjectId(usuario_rol['usuario_id'])})
                
                if usuario_contrata:
                    contratas_info = {
                        '_id': uc['_id'],
                        'contrata_info': {
                            'alias': uc['alias_usuario_contrata'],
                            'estado_usuario_contrata': uc['estado_usuario_contrata']
                        },
                        'email': usuario_contrata['email'],
                        'nombre_usuario': usuario_contrata.get('nombre_usuario', '')
                    }
                    usuarios_contratas.append(contratas_info)

        return render_template('usuarios_gestores/usuarios_contratas/listar.html',
                               usuarios_contratas=usuarios_contratas,
                               contrata_id=contrata_id,
                               gestor_id=gestor_id,
                               nombre_gestor=nombre_gestor,
                               titular=titular
                            )

    except Exception as e:
        flash(f'Error al listar los usuarios contratas: {str(e)}', 'danger')
        return redirect(url_for('ug_contratas.contratas_contrata', gestor_id=gestor_id, titular_id=titular_id, contrata_id=contrata_id))

def usuarios_contratas_crear_vista(gestor_id, titular_id, contrata_id):
    return render_template('usuarios_gestores/usuarios_contratas/crear.html', gestor_id=gestor_id, titular_id=titular_id, contrata_id=contrata_id)

def usuarios_contratas_actualizar_vista(gestor_id, titular_id, contrata_id, usuario_contrata_id):
    return render_template('usuarios_gestores/usuarios_contratas/actualizar.html', gestor_id=gestor_id, titular_id=titular_id, contrata_id=contrata_id, usuario_contrata_id=usuario_contrata_id)

def usuarios_contratas_eliminar_vista(gestor_id, titular_id, contrata_id, usuario_contrata_id):
    return render_template('usuarios_gestores/usuarios_contratas/eliminar.html')


