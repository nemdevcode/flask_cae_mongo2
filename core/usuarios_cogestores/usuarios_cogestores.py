from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from utils.usuario_utils import obtener_usuario_autenticado
from utils.rol_utils import verificar_rol_cogestor
from config import conexion_mongo

db = conexion_mongo()

def usuarios_cogestores_vista():
    '''
    Vista para mostrar los gestores relacionados con el usuario el usuario gestor que los gestiona. 
    Muestra los gestores activos y permite filtrar por la informacion contenida en la variable filtrar_gestor y por estado.
    '''
    try:
        # Obtener usuario autenticado y verificar permisos
        usuario, respuesta_redireccion = obtener_usuario_autenticado()
        if respuesta_redireccion:
            return respuesta_redireccion
        
        # Verificar rol de cogestor
        tiene_rol, usuario_rol_cogestor_id = verificar_rol_cogestor(usuario['_id'])
        if not tiene_rol:
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('usuarios.usuarios'))
        
        # Obtener parámetros de filtrado
        filtrar_usuario_gestor = request.form.get('filtrar_usuario_gestor', '')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('usuarios_cogestores.usuarios_cogestores'))
        
        # Obtener todos los usuarios con rol de gestor relacionados al usuario cogestor
        usuarios_rol_gestor_id = list(db.usuarios_cogestores.find(
            {'usuario_rol_cogestor_id': usuario_rol_cogestor_id}, 
            {'usuario_rol_gestor_id': 1}
        ))
        print(f"usuarios_rol_gestor_id: {usuarios_rol_gestor_id}")

        # Obtener los usuarios con rol de gestor de la coleccion usuarios_roles
        usuarios_gestores = []
        for usuario_gestor_id in usuarios_rol_gestor_id:
            # Obtener el usuario_rol del gestor
            usuario_rol_gestor = db.usuarios_roles.find_one(
                {'_id': usuario_gestor_id['usuario_rol_gestor_id']}
            )
            if usuario_rol_gestor:
                # Obtener el usuario asociado al rol de gestor
                usuario = db.usuarios.find_one(
                    {'_id': usuario_rol_gestor['usuario_id']}
                )
                if usuario:
                    # Aplicar filtro si existe
                    if filtrar_usuario_gestor:
                        filtro = filtrar_usuario_gestor.lower()
                        if (filtro not in usuario.get('nombre_usuario', '').lower() and
                            filtro not in usuario.get('email', '').lower() and
                            filtro not in usuario.get('telefono_usuario', '').lower()):
                            continue
                    
                    usuarios_gestores.append({
                        'usuario_rol_id': usuario_rol_gestor['_id'],
                        'usuario_id': usuario['_id'],
                        'nombre_usuario': usuario.get('nombre_usuario', ''),
                        'email': usuario.get('email', ''),
                        'telefono_usuario': usuario.get('telefono_usuario', '')
                    })
        print(f"usuarios_gestores: {usuarios_gestores}")

        return render_template('usuarios/usuarios_cogestores.html',
                               usuarios_gestores=usuarios_gestores,
                               usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                               filtrar_usuario_gestor=filtrar_usuario_gestor
                               )
    
    except Exception as e:
        flash(f'Error al cargar la vista de usuarios cogestores: {str(e)}', 'danger')
        return redirect(url_for('usuarios.usuarios'))

def usuarios_cogestores_gestor_vista(usuario_rol_id, usuario_rol_gestor_id, gestor_id):
    '''
    Vista del gestor seleccionado relacionados con el usuario cogestor autenticado.
    '''
    pass