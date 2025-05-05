from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from datetime import datetime
from config import conexion_mongo

db = conexion_mongo()

def centros_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    '''
    Vista para listar los centros del gestor asignado como cogestor
    '''
    try:
         # Obtener parámetros de filtrado
        filtrar_centro = request.form.get('filtrar_centro', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')
        
        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('uc_centros.centros', 
                                    usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                                    usuario_rol_gestor_id=usuario_rol_gestor_id, 
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id))
        
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

        # Obtener el nombre del titular seleccionado
        nombre_titular = db.titulares.find_one({
            '_id': ObjectId(titular_id)
        }, {'nombre_titular': 1, '_id': 0})


        return render_template('usuarios_cogestores/centros/listar.html', 
                               usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                               usuario_rol_gestor_id=usuario_rol_gestor_id, 
                               gestor_id=gestor_id, 
                               titular_id=titular_id,
                               nombre_titular=nombre_titular.get('nombre_titular'),
                               centros=centros,
                               filtrar_centro=filtrar_centro,
                               filtrar_estado=filtrar_estado
                               )
    except Exception as e:
        print(f"Error en centros_vista: {e}")
        return render_template('usuarios_cogestores/centros/listar.html', 
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                           usuario_rol_gestor_id=usuario_rol_gestor_id, 
                           gestor_id=gestor_id, 
                           titular_id=titular_id)

def crear_centro(titular_id, datos_formulario):
    '''
    Crea un nuevo centro en la base de datos.
    '''
    try:
         # Obtener los datos del formulario
        nombre_centro = datos_formulario.get('nombre_centro')
        domicilio = datos_formulario.get('domicilio')
        codigo_postal = datos_formulario.get('codigo_postal')
        poblacion = datos_formulario.get('poblacion')
        provincia = datos_formulario.get('provincia')
        telefono_centro = datos_formulario.get('telefono_centro')

        # Insertar el titular en la base de datos
        insert = db.centros.insert_one({
            'titular_id': ObjectId(titular_id),
            'nombre_centro': nombre_centro,
            'domicilio': domicilio,
            'codigo_postal': codigo_postal,
            'poblacion': poblacion,
            'provincia': provincia,
            'telefono_centro': telefono_centro,
            'fecha_activacion': datetime.now(),
            'fecha_modificacion': datetime.now(),
            'fecha_inactivacion': None,
            'estado_centro': 'activo'
        })

        if insert.inserted_id:
            flash('Centro creado exitosamente', 'success')
            return True, None
        else:
            flash('Error al crear el centro', 'danger')
            return False, datos_formulario
        
    except Exception as e:
        flash(f'Error al procesar el formulario: {str(e)}', 'danger')
        return False, datos_formulario

def centros_crear_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    '''
    Vista para crear un centro
    '''
    try:
        # Si es una petición POST, procesar el formulario
        if request.method == 'POST':
            creado, datos_formulario = crear_centro(titular_id, request.form)
            if creado:
                return redirect(url_for('uc_centros.centros',
                                        usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                        usuario_rol_gestor_id=usuario_rol_gestor_id,
                                        gestor_id=gestor_id,
                                        titular_id=titular_id))
            else:
                return render_template('usuarios_cogestores/centros/crear.html',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id,
                                datos_formulario=datos_formulario)
            
        # Si es una petición GET, mostrar el formulario vacío
        return render_template('usuarios_cogestores/centros/crear.html',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id)

    except Exception as e:
        flash(f'Error al crear el centro: {str(e)}', 'danger')
        return redirect(url_for('uc_centros.centros',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id))

def actualizar_centro(centro_id, datos_formulario):
    '''
    Actualiza un centro existente en la base de datos.
    '''
    try:
        # Obtener los datos del formulario
        nombre_centro = datos_formulario.get('nombre_centro')
        domicilio = datos_formulario.get('domicilio')
        codigo_postal = datos_formulario.get('codigo_postal')
        poblacion = datos_formulario.get('poblacion')
        provincia = datos_formulario.get('provincia')
        telefono_centro = datos_formulario.get('telefono_centro')
        estado_centro = datos_formulario.get('estado_centro')

        # Actualizar el centro en la base de datos
        update = db.centros.update_one({
            '_id': ObjectId(centro_id)
        }, {
            '$set': {
                'nombre_centro': nombre_centro,
                'domicilio': domicilio,
                'codigo_postal': codigo_postal,
                'poblacion': poblacion,
                'provincia': provincia,
                'telefono_centro': telefono_centro,
                'fecha_modificacion': datetime.now(),
                'fecha_inactivacion': None,
                'estado_centro': estado_centro
            }
        })

        if update.modified_count > 0:
            flash('Centro actualizado exitosamente', 'success')
            return True, None
        else:
            flash('Error al actualizar el centro', 'danger')
            return False, datos_formulario
        
    except Exception as e:
        flash(f'Error al actualizar el centro: {str(e)}', 'danger')
        return False, datos_formulario
    
def centros_actualizar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id):
    '''
    Vista para actualizar un centro
    '''
    try:
        # Obtener el centro a actualizar
        centro = db.centros.find_one({
            '_id': ObjectId(centro_id)
        })

        # Si es una petición POST, procesar el formulario
        if request.method == 'POST':
            actualizado, datos_formulario = actualizar_centro(centro_id, request.form)
            if actualizado:
                return redirect(url_for('uc_centros.centros',
                                        usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                        usuario_rol_gestor_id=usuario_rol_gestor_id,
                                        gestor_id=gestor_id,
                                        titular_id=titular_id,
                                        centro_id=centro_id
                                        ))
            else:
                return render_template('usuarios_cogestores/centros/actualizar.html',
                                        usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                        usuario_rol_gestor_id=usuario_rol_gestor_id,
                                        gestor_id=gestor_id,
                                        titular_id=titular_id,
                                        centro_id=centro_id,
                                        centro=centro
                                        )

        return render_template('usuarios_cogestores/centros/actualizar.html', 
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                           usuario_rol_gestor_id=usuario_rol_gestor_id, 
                           gestor_id=gestor_id, 
                           titular_id=titular_id, 
                           centro_id=centro_id,
                           centro=centro
                           )

    except Exception as e:
        flash(f'Error al actualizar el centro: {str(e)}', 'danger')
        return redirect(url_for('uc_centros.centros',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id
                                ))

def centros_eliminar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id):
    '''
    Vista para eliminar un centro
    '''
    try:
        # Eliminar el centro
        delete = db.centros.delete_one({
            '_id': ObjectId(centro_id)
        })

        if delete.deleted_count > 0:
            flash('Centro eliminado exitosamente', 'success')
            return redirect(url_for('uc_centros.centros',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id
                                ))
        else:
            flash('Error al eliminar el centro', 'danger')
            return redirect(url_for('uc_centros.centros',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id
                                ))

    except Exception as e:
        flash(f'Error al eliminar el centro: {str(e)}', 'danger')
        return redirect(url_for('uc_centros.centros',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id
                                ))

def centros_centro_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id):
    return render_template('usuarios_cogestores/centros/index.html', 
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                           usuario_rol_gestor_id=usuario_rol_gestor_id, 
                           gestor_id=gestor_id, 
                           titular_id=titular_id, 
                           centro_id=centro_id
                           )


