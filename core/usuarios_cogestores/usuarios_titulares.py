from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from utils.usuario_utils import obtener_usuario_autenticado
from utils.rol_utils import verificar_rol_cogestor
from config import conexion_mongo

db = conexion_mongo()

def usuarios_titulares_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    '''
    Vista para mostrar los usuarios titulares de un titular
    '''
    try:
        # Obtener nombre del titular
        nombre_titular = db.titulares.find_one({'_id': ObjectId(titular_id)})['nombre_titular']

        # Obtener parámetros de filtrado
        filtrar_usuario_titular = request.form.get('filtrar_usuario_titular', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('uc_usuarios_titulares.usuarios_titulares', 
                                    usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                    usuario_rol_gestor_id=usuario_rol_gestor_id,
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id
                                    ))
        
        # Construir la consulta base - buscar usuarios titulares donde el titular_id sea el del titular actual
        query = {'titular_id': ObjectId(titular_id)}
        
        # Aplicar filtros si existen
        if filtrar_usuario_titular:
            query['alias_usuario_titular'] = {'$regex': filtrar_usuario_titular, '$options': 'i'}

        if filtrar_estado != 'todos':
            query['estado_usuario_titular'] = filtrar_estado
        

        # Obtener los usuarios titulares asociados al titular_id
        usuarios_titulares = []
        usuarios_titulares_cursor = db.usuarios_titulares.find(query)

        for ut in usuarios_titulares_cursor:
            # Obtener el usuario_rol del titular usando la función obtener_usuario_rol
            usuario_rol_titular = db.usuarios_roles.find_one({'_id': ut['usuario_rol_titular_id']})
            
            if usuario_rol_titular:
                # Obtener la información del usuario titular
                usuario_titular = db.usuarios.find_one({'_id': ObjectId(usuario_rol_titular['usuario_id'])})
                
                if usuario_titular:
                    titular_info = {
                        '_id': ut['_id'],
                        'titular_info': {
                            'alias': ut['alias_usuario_titular'],
                            'estado_usuario_titular': ut['estado_usuario_titular']
                        },
                        'email': usuario_titular['email'],
                        'nombre_usuario': usuario_titular.get('nombre_usuario', '')
                    }
                    usuarios_titulares.append(titular_info)

        return render_template('usuarios_cogestores/usuarios_titulares/listar.html',
                            usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                            usuario_rol_gestor_id=usuario_rol_gestor_id, 
                            gestor_id=gestor_id, 
                            titular_id=titular_id,
                            nombre_titular=nombre_titular,
                            usuarios_titulares=usuarios_titulares
                            )
    except Exception as e:
        flash(f'Error al listar los usuarios titulares: {str(e)}', 'danger')
        return redirect(url_for('uc_usuarios_titulares.usuarios_titulares', 
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id, 
                                titular_id=titular_id
                                ))
def crear_usuario_titular(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    '''
    Función para crear un usuario titular
    '''
    return render_template('usuarios_cogestores/usuarios_titulares/crear.html',
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                           usuario_rol_gestor_id=usuario_rol_gestor_id, 
                           gestor_id=gestor_id, 
                           titular_id=titular_id
                           )
def usuarios_titulares_crear_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    '''
    Vista para crear un usuario titular
    '''
    return render_template('usuarios_cogestores/usuarios_titulares/crear.html',
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                           usuario_rol_gestor_id=usuario_rol_gestor_id, 
                           gestor_id=gestor_id, 
                           titular_id=titular_id
                           )

def actualizar_usuario_titular(usuario_titular_id, datos_formulario):
    '''
    Función para actualizar un usuario titular
    '''
    try:
        # Obtener los datos del formulario
        alias = datos_formulario.get('alias', '').strip().upper()
        estado_usuario_titular = datos_formulario.get('estado_usuario_titular', 'activo')

        # Actualizar el usuario titular
        actualizar = db.usuarios_titulares.update_one(
            {'_id': ObjectId(usuario_titular_id)},
            {'$set': {
                'alias_usuario_titular': alias,
                'estado_usuario_titular': estado_usuario_titular
            }}
        )

        if actualizar.modified_count > 0:
            flash('Usuario titular actualizado exitosamente', 'success')
            return True, None
        else:
            flash('No se realizaron cambios en el usuario titular', 'info')
            return True, None

    except Exception as e:
        flash(f'Error al actualizar el usuario titular: {str(e)}', 'danger')
        return False, datos_formulario


def usuarios_titulares_actualizar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, usuario_titular_id):
    '''
    Vista para actualizar un usuario titular
    '''
    try:
        # Obtener el usuario titular a actualizar
        usuario_titular = db.usuarios_titulares.find_one({'_id': ObjectId(usuario_titular_id)})
        # Obtener el usuario_rol del titular
        usuario_rol = db.usuarios_roles.find_one({'_id': usuario_titular['usuario_rol_titular_id']})
         # Obtener la información del usuario titular
        usuario = db.usuarios.find_one({'_id': ObjectId(usuario_rol['usuario_id'])})
        # Preparar la información del usuario titular en el formato que espera el template
        usuario_titular_info = {
            '_id': usuario_titular['_id'],
            'titular_info': {
                'alias': usuario_titular['alias_usuario_titular'],
                'estado_usuario_titular': usuario_titular['estado_usuario_titular']
            },
            'email': usuario['email']
        }
        # Si es una petición POST, procesar el formulario
        if request.method == 'POST':
            actualizar = actualizar_usuario_titular(usuario_titular_id, request.form)
            if actualizar:
                return redirect(url_for('uc_usuarios_titulares.usuarios_titulares', 
                                        usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                        usuario_rol_gestor_id=usuario_rol_gestor_id,
                                        gestor_id=gestor_id, 
                                        titular_id=titular_id, 
                                        usuario_titular_id=usuario_titular_id,
                                        usuario_titular=usuario_titular_info
                                        ))
            else:
                return render_template('usuarios_cogestores/usuarios_titulares/actualizar.html',
                                       usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                                       usuario_rol_gestor_id=usuario_rol_gestor_id, 
                                       gestor_id=gestor_id, 
                                       usuario_titular_id=usuario_titular_id,
                                       usuario_titular=usuario_titular_info
                                       )
        return render_template('usuarios_cogestores/usuarios_titulares/actualizar.html',
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                           usuario_rol_gestor_id=usuario_rol_gestor_id, 
                           gestor_id=gestor_id, 
                           usuario_titular_id=usuario_titular_id,
                           usuario_titular=usuario_titular_info
                           )
    except Exception as e:
        flash(f'Error al actualizar el usuario titular: {str(e)}', 'danger')
        return redirect(url_for('uc_usuarios_titulares.usuarios_titulares', 
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id, 
                                titular_id=titular_id, 
                                usuario_titular_id=usuario_titular_id
                                ))


def usuarios_titulares_eliminar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, usuario_titular_id):
    '''
    Vista para eliminar un usuario titular
    '''
    return render_template('usuarios_cogestores/usuarios_titulares/eliminar.html',
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                           usuario_rol_gestor_id=usuario_rol_gestor_id, 
                           gestor_id=gestor_id, 
                           titular_id=titular_id, 
                           usuario_titular_id=usuario_titular_id
                           )





