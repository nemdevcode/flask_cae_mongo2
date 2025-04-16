from flask import render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from datetime import datetime

from utils.usuario_utils import obtener_usuario_autenticado
from utils.gestor_utils import obtener_gestor_por_usuario
from utils.rol_utils import verificar_rol_gestor

from config import conexion_mongo

db = conexion_mongo()

def verificaciones_consultas(gestor_id, titular_id):
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
    titular = db.titulares.find_one({'_id': ObjectId(titular_id)})
    if not titular:
        flash('Titular no encontrado o no pertenece a este gestor', 'danger')
        return False, redirect(url_for('ug_titulares.titulares', gestor_id=gestor_id))
    
    return True, (usuario, usuario_rol_id, gestor, titular)

def centros_vista(gestor_id, titular_id):
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id)
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_id, gestor, titular = resultado
        nombre_gestor = gestor.get('nombre_gestor', 'Gestor')
        
        # Obtener parámetros de filtrado
        filtrar_centro = request.form.get('filtrar_centro', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')
        
        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('ug_centros.centros', gestor_id=gestor_id, titular_id=titular_id))
        
        # Construir la consulta base - buscar centros donde el titular_id sea el del titular actual
        consulta_filtros = {'titular_id': ObjectId(titular_id)}
        
        # Aplicar filtros si existen
        if filtrar_estado != 'todos':
            consulta_filtros['estado_centro'] = filtrar_estado
        
        # Obtener los centros asociados al titular
        centros = []
        centros_titular = db.centros.find(consulta_filtros)
        
        for centro in centros_titular:
            # Si hay filtro por texto, verificar si coincide en algún campo
            if filtrar_centro:
                if (filtrar_centro.lower() not in centro['nombre_centro'].lower() and
                    filtrar_centro.lower() not in centro['domicilio'].lower() and
                    filtrar_centro.lower() not in centro['codigo_postal'].lower() and
                    filtrar_centro.lower() not in centro['poblacion'].lower() and
                    filtrar_centro.lower() not in centro['provincia'].lower() and
                    filtrar_centro.lower() not in centro.get('telefono_centro', '').lower()):
                    continue

            centros.append({
                '_id': str(centro['_id']),
                'nombre_centro': centro['nombre_centro'],
                'domicilio': centro['domicilio'],
                'codigo_postal': centro['codigo_postal'],
                'poblacion': centro['poblacion'],
                'provincia': centro['provincia'],
                'telefono_centro': centro.get('telefono_centro', ''),
                'estado_centro': centro.get('estado_centro', centro.get('estado', 'activo'))
            })

        return render_template('usuarios_gestores/centros/listar.html',
                               centros=centros,
                               titular=titular,
                               nombre_gestor=nombre_gestor,
                               filtrar_centro=filtrar_centro,
                               filtrar_estado=filtrar_estado,
                               gestor_id=gestor_id
                               )
                             
    except Exception as e:
        flash(f'Error al cargar los centros: {str(e)}', 'danger')
        return redirect(url_for('ug_titulares.titulares_titular', gestor_id=gestor_id, titular_id=titular_id))

def crear_centro(gestor_id, titular_id, form_data):
    """
    Crea un nuevo centro en la base de datos.
    
    Args:
        gestor_id (str): ID del gestor
        titular_id (str): ID del titular
        form_data (dict): Datos del formulario
    
    Returns:
        tuple: (bool, dict) 
            - bool: True si se creó exitosamente, False si hubo error
            - dict: Datos del formulario o mensaje de error
    """
    try:
        # Obtener datos del formulario
        nombre_centro = form_data.get('nombre_centro', '').strip().upper()
        domicilio = form_data.get('domicilio', '').strip()
        codigo_postal = form_data.get('codigo_postal', '').strip()
        poblacion = form_data.get('poblacion', '').strip().upper()
        provincia = form_data.get('provincia', '').strip().upper()
        telefono_centro = form_data.get('telefono_centro', '').strip()
        
        # Verificar si ya existe un centro con el mismo nombre para este titular
        centro_existente = db.centros.find_one({
            'titular_id': ObjectId(titular_id),
            'nombre_centro': nombre_centro
        })
        if centro_existente:
            flash('Ya existe un centro con este nombre para este titular', 'warning')
            return False, form_data
            
        # Crear el centro
        centro = {
            'titular_id': ObjectId(titular_id),
            'nombre_centro': nombre_centro,
            'domicilio': domicilio,
            'codigo_postal': codigo_postal,
            'poblacion': poblacion,
            'provincia': provincia,
            'telefono_centro': telefono_centro,
            'estado_centro': 'activo',
            'fecha_activacion': datetime.now(),
            'fecha_modificacion': datetime.now()
        }

        # Insertar el centro
        insert = db.centros.insert_one(centro)
        if insert.inserted_id:
            flash('Centro creado correctamente', 'success')
            return True, None
        else:
            flash('Error al crear el centro', 'danger')
            return False, form_data

    except Exception as e:
        flash(f'Error al crear el centro: {str(e)}', 'danger')
        return False, form_data

def centros_crear_vista(gestor_id, titular_id):
    
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id)
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_id, gestor, titular = resultado
        nombre_gestor = gestor.get('nombre_gestor', 'Gestor')
        
        # Convertir los ObjectId a string para el template
        gestor_id = str(gestor_id)
        titular_id = str(titular_id)
        titular['_id'] = str(titular['_id'])

        if request.method == 'GET':
            return render_template('usuarios_gestores/centros/crear.html',
                                 gestor_id=gestor_id,
                                 titular_id=titular_id,
                                 usuario=usuario,
                                 usuario_rol_id=usuario_rol_id,
                                 gestor=gestor,
                                 titular=titular,
                                 nombre_gestor=nombre_gestor
                                 )

        if request.method == 'POST':
            # Procesar el formulario con la función crear_centro
            creado, datos_formulario = crear_centro(gestor_id, titular_id, request.form)
            if creado:
                return redirect(url_for('ug_centros.centros', gestor_id=gestor_id, titular_id=titular_id))
            else:
                return render_template('usuarios_gestores/centros/crear.html',
                                     gestor_id=gestor_id,
                                     titular_id=titular_id,
                                     usuario=usuario,
                                     usuario_rol_id=usuario_rol_id,
                                     gestor=gestor,
                                     titular=titular,
                                     nombre_gestor=nombre_gestor,
                                     form_data=datos_formulario
                                     )

    except Exception as e:
        flash(f'Error al crear el centro: {str(e)}', 'danger')
        return redirect(url_for('ug_centros.centros', gestor_id=gestor_id, titular_id=titular_id))

def actualizar_centro(centro_id, form_data):
    """
    Actualiza un centro existente en la base de datos.
    
    Args:
        centro_id (str): ID del centro a actualizar
        form_data (dict): Datos del formulario
    
    Returns:
        tuple: (bool, dict) 
            - bool: True si se actualizó exitosamente, False si hubo error
            - dict: Datos del formulario o mensaje de error
    """
    try:
        # Obtener datos del formulario
        nombre_centro = form_data.get('nombre_centro', '').strip().upper()
        domicilio = form_data.get('domicilio', '').strip()
        codigo_postal = form_data.get('codigo_postal', '').strip()
        poblacion = form_data.get('poblacion', '').strip().upper()
        provincia = form_data.get('provincia', '').strip().upper()
        telefono_centro = form_data.get('telefono_centro', '').strip()
        estado_centro = form_data.get('estado_centro', 'activo')
        # Validar datos
        if not all([nombre_centro, domicilio, codigo_postal, poblacion, provincia]):
            flash('Todos los campos son obligatorios', 'danger')
            return False, form_data

        # Actualizar el centro
        resultado = db.centros.update_one(
            {'_id': ObjectId(centro_id)},
            {
                '$set': {
                    'nombre_centro': nombre_centro,
                    'domicilio': domicilio,
                    'codigo_postal': codigo_postal,
                    'poblacion': poblacion,
                    'provincia': provincia,
                    'telefono_centro': telefono_centro,
                    'estado_centro': estado_centro,
                    'fecha_modificacion': datetime.now()
                }
            }
        )
        
        if resultado.modified_count > 0:
            flash('Centro actualizado correctamente', 'success')
            return True, None
        else:
            flash('No se realizaron cambios en el centro', 'info')
            return True, None

    except Exception as e:
        flash(f'Error al actualizar el centro: {str(e)}', 'danger')
        return False, form_data

def centros_actualizar_vista(gestor_id, titular_id, centro_id):
    
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id)
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_id, gestor, titular = resultado
        nombre_gestor = gestor.get('nombre_gestor', 'Gestor')
        
        # Convertir IDs a string para el template
        titular['_id'] = str(titular['_id'])
        
        # Obtener el centro
        centro = db.centros.find_one({'_id': ObjectId(centro_id)})
        if not centro:
            flash('Centro no encontrado', 'danger')
            return redirect(url_for('ug_centros.centros', gestor_id=gestor_id, titular_id=titular_id))
            
        # Convertir IDs a string para el template
        centro['_id'] = str(centro['_id'])
        centro['titular_id'] = str(centro['titular_id'])

        if request.method == 'GET':
            return render_template('usuarios_gestores/centros/actualizar.html',
                                 gestor_id=gestor_id,
                                 titular_id=titular_id,
                                 usuario=usuario,
                                 usuario_rol_id=usuario_rol_id,
                                 gestor=gestor,
                                 titular=titular,
                                 nombre_gestor=nombre_gestor,
                                 centro=centro
                                 )

        if request.method == 'POST':
            # Procesar el formulario con la función actualizar_centro
            actualizado, datos_formulario = actualizar_centro(centro_id, request.form)
            if actualizado:
                return redirect(url_for('ug_centros.centros', gestor_id=gestor_id, titular_id=titular_id))
            else:
                return render_template('usuarios_gestores/centros/actualizar.html',
                                     gestor_id=gestor_id,
                                     titular_id=titular_id,
                                     usuario=usuario,
                                     usuario_rol_id=usuario_rol_id,
                                     gestor=gestor,
                                     titular=titular,
                                     nombre_gestor=nombre_gestor,
                                     centro=centro,
                                     form_data=datos_formulario
                                     )

    except Exception as e:
        flash(f'Error al actualizar el centro: {str(e)}', 'danger')
        return redirect(url_for('ug_centros.centros', gestor_id=gestor_id, titular_id=titular_id))

def eliminar_centro(centro_id):
    """
    Elimina un centro de la base de datos.
    
    Args:
        centro_id (str): ID del centro a eliminar
    
    Returns:
        bool: True si se eliminó exitosamente, False si hubo error
    """
    try:
        # Verificar si el centro existe
        centro = db.centros.find_one({'_id': ObjectId(centro_id)})
        if not centro:
            flash('Centro no encontrado', 'danger')
            return False
            
        # Eliminar el centro
        delete = db.centros.delete_one({'_id': ObjectId(centro_id)})
        if delete.deleted_count > 0:
            flash('Centro eliminado correctamente', 'success')
            return True
        else:
            flash('Error al eliminar el centro', 'danger')
            return False

    except Exception as e:
        flash(f'Error al eliminar el centro: {str(e)}', 'danger')
        return False

def centros_eliminar_vista(gestor_id, titular_id, centro_id):
    
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id)
        if not permisos_ok:
            return resultado
            
        # Ejecutar la eliminación
        eliminado = eliminar_centro(centro_id)
        if eliminado:
            return redirect(url_for('ug_centros.centros', gestor_id=gestor_id, titular_id=titular_id))
        else:
            return redirect(url_for('ug_centros.centros', gestor_id=gestor_id, titular_id=titular_id))

    except Exception as e:
        flash(f'Error al eliminar el centro: {str(e)}', 'danger')
        return redirect(url_for('ug_centros.centros', gestor_id=gestor_id, titular_id=titular_id))
    
def centros_centro_vista(gestor_id, titular_id, centro_id):
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id)
        if not permisos_ok:
            return resultado
        
        # Verificar que el centro pertenece al titular actual
        centro = db.centros.find_one({
            '_id': ObjectId(centro_id),
            'titular_id': ObjectId(titular_id)
        })
        if not centro:
            flash('Centro no encontrado o no pertenece a este titular', 'danger')
            return redirect(url_for('ug_centros.centros', gestor_id=gestor_id, titular_id=titular_id))
        
        return render_template('usuarios_gestores/centros/index.html',
                               centro=centro,
                               gestor_id=gestor_id,
                               titular_id=titular_id)
    except Exception as e:
        flash(f'Error al cargar el centro: {str(e)}', 'danger')
        return redirect(url_for('ug_centros.centros', gestor_id=gestor_id, titular_id=titular_id))
    