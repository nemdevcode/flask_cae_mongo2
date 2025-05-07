from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from datetime import datetime
from config import conexion_mongo

db = conexion_mongo()

def contratas_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    '''
    Vista para listar las contratas del titular asignado como cogestor
    '''
    try:
        # Obtener parámetros de filtrado
        filtrar_contrata = request.form.get('filtrar_contrata', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')
        
        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('uc_contratas.contratas', 
                                    usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                                    usuario_rol_gestor_id=usuario_rol_gestor_id, 
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id
                                    ))
        
        # Construir la consulta base - buscar centros donde el titular_id sea el del titular actual
        consulta_filtros = {'titular_id': ObjectId(titular_id)}
        
        # Aplicar filtros si existen
        if filtrar_estado != 'todos':
            consulta_filtros['estado_centro'] = filtrar_estado
        
        # Obtener las contratas asociadas al titular
        contratas = []
        contratas_titular = db.contratas.find(consulta_filtros)
        
        for contrata in contratas_titular:
            # Si hay filtro por texto, verificar si coincide en algún campo
            if filtrar_contrata:
                if (filtrar_contrata.lower() not in contrata['nombre_contrata'].lower() and
                    filtrar_contrata.lower() not in contrata['cif_dni'].lower() and
                    filtrar_contrata.lower() not in contrata['domicilio'].lower() and
                    filtrar_contrata.lower() not in contrata['codigo_postal'].lower() and
                    filtrar_contrata.lower() not in contrata['poblacion'].lower() and
                    filtrar_contrata.lower() not in contrata['provincia'].lower() and
                    filtrar_contrata.lower() not in contrata.get('telefono_contrata', '').lower()):
                    continue

            contratas.append({
                '_id': str(contrata['_id']),
                'nombre_contrata': contrata['nombre_contrata'],
                'cif_dni': contrata['cif_dni'],
                'domicilio': contrata['domicilio'],
                'codigo_postal': contrata['codigo_postal'],
                'poblacion': contrata['poblacion'],
                'provincia': contrata['provincia'],
                'telefono_contrata': contrata.get('telefono_contrata', ''),
                'estado_contrata': contrata.get('estado_contrata', contrata.get('estado', 'activo'))
            })

        # Obtener el nombre del titular seleccionado
        nombre_titular = db.titulares.find_one({
            '_id': ObjectId(titular_id)
        }, {'nombre_titular': 1, '_id': 0})


        return render_template('usuarios_cogestores/contratas/listar.html', 
                               usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                               usuario_rol_gestor_id=usuario_rol_gestor_id, 
                               gestor_id=gestor_id, 
                               titular_id=titular_id,
                               nombre_titular=nombre_titular.get('nombre_titular'),
                               contratas=contratas,
                               filtrar_contrata=filtrar_contrata,
                               filtrar_estado=filtrar_estado
                               )
    except Exception as e:
        flash(f'Error al cargar la vista de contratas: {str(e)}', 'danger')
        return render_template('usuarios_cogestores/contratas/listar.html', 
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                           usuario_rol_gestor_id=usuario_rol_gestor_id, 
                           gestor_id=gestor_id, 
                           titular_id=titular_id)

def crear_contrata(titular_id, datos_formulario):
    '''
    Crea una nueva contrata en la base de datos.
    '''
    try:
         # Obtener los datos del formulario
        nombre_contrata = datos_formulario.get('nombre_contrata')
        cif_dni = datos_formulario.get('cif_dni')
        domicilio = datos_formulario.get('domicilio')
        codigo_postal = datos_formulario.get('codigo_postal')
        poblacion = datos_formulario.get('poblacion')
        provincia = datos_formulario.get('provincia')
        telefono_contrata = datos_formulario.get('telefono_contrata')
        email_contrata = datos_formulario.get('email_contrata')

        # Insertar la contrata en la base de datos
        insert = db.contratas.insert_one({
            'titular_id': ObjectId(titular_id),
            'nombre_contrata': nombre_contrata,
            'cif_dni': cif_dni,
            'domicilio': domicilio,
            'codigo_postal': codigo_postal,
            'poblacion': poblacion,
            'provincia': provincia,
            'telefono_contrata': telefono_contrata,
            'fecha_activacion': datetime.now(),
            'fecha_modificacion': datetime.now(),
            'fecha_inactivacion': None,
            'estado_contrata': 'activo',
            'email_contrata': email_contrata
        })

        if insert.inserted_id:
            flash('Contrata creada correctamente', 'success')
            return True, None
        else:
            flash('Error al crear la contrata', 'danger')
            return False, datos_formulario
        
    except Exception as e:
        flash(f'Error al procesar el formulario: {str(e)}', 'danger')
        return False, datos_formulario

def contratas_crear_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    '''
    Vista para crear una contrata
    '''
    try:
        # Si es una petición POST, procesar el formulario
        if request.method == 'POST':
            creado, datos_formulario = crear_contrata(titular_id, request.form)
            if creado:
                return redirect(url_for('uc_contratas.contratas',
                                        usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                        usuario_rol_gestor_id=usuario_rol_gestor_id,
                                        gestor_id=gestor_id,
                                        titular_id=titular_id))
            else:
                return render_template('usuarios_cogestores/contratas/crear.html',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id,
                                datos_formulario=datos_formulario)
            
        # Si es una petición GET, mostrar el formulario vacío
        return render_template('usuarios_cogestores/contratas/crear.html',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id)

    except Exception as e:
        flash(f'Error al crear la contrata: {str(e)}', 'danger')
        return redirect(url_for('uc_contratas.contratas',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id))

def actualizar_contrata(contrata_id, datos_formulario):
    '''
    Actualiza una contratación existente en la base de datos.
    '''
    try:
        # Obtener los datos del formulario
        nombre_contrata = datos_formulario.get('nombre_contrata')
        cif_dni = datos_formulario.get('cif_dni')
        domicilio = datos_formulario.get('domicilio')
        codigo_postal = datos_formulario.get('codigo_postal')
        poblacion = datos_formulario.get('poblacion')
        provincia = datos_formulario.get('provincia')
        telefono_contrata = datos_formulario.get('telefono_contrata')
        estado_contrata = datos_formulario.get('estado_contrata')
        email_contrata = datos_formulario.get('email_contrata')

        # Actualizar la contratación en la base de datos
        update = db.contratas.update_one({
            '_id': ObjectId(contrata_id)
        }, {
            '$set': {
                'nombre_contrata': nombre_contrata,
                'cif_dni': cif_dni,
                'domicilio': domicilio,
                'codigo_postal': codigo_postal,
                'poblacion': poblacion,
                'provincia': provincia,
                'telefono_contrata': telefono_contrata,
                'fecha_modificacion': datetime.now(),
                'fecha_inactivacion': None,
                'estado_contrata': estado_contrata,
                'email_contrata': email_contrata
            }
        })

        if update.modified_count > 0:
            flash('Contrata actualizada exitosamente', 'success')
            return True, None
        else:
            flash('Error al actualizar la contratación', 'danger')
            return False, datos_formulario
        
    except Exception as e:
        flash(f'Error al actualizar la contratación: {str(e)}', 'danger')
        return False, datos_formulario

def contratas_actualizar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id):
    '''
    Vista para actualizar una contrata
    '''
    try:
        # Obtener la contrata a actualizar
        contrata = db.contratas.find_one({
            '_id': ObjectId(contrata_id)
        })

        # Si es una petición POST, procesar el formulario
        if request.method == 'POST':
            actualizado, datos_formulario = actualizar_contrata(contrata_id, request.form)
            if actualizado:
                return redirect(url_for('uc_contratas.contratas',
                                        usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                        usuario_rol_gestor_id=usuario_rol_gestor_id,
                                        gestor_id=gestor_id,
                                        titular_id=titular_id,
                                        contrata_id=contrata_id
                                        ))
            else:
                return render_template('usuarios_cogestores/contratas/actualizar.html',
                                        usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                        usuario_rol_gestor_id=usuario_rol_gestor_id,
                                        gestor_id=gestor_id,
                                        titular_id=titular_id,
                                        contrata_id=contrata_id,
                                        contrata=contrata
                                        )

        return render_template('usuarios_cogestores/contratas/actualizar.html', 
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                           usuario_rol_gestor_id=usuario_rol_gestor_id, 
                           gestor_id=gestor_id, 
                           titular_id=titular_id, 
                           contrata_id=contrata_id,
                           contrata=contrata
                           )

    except Exception as e:
        flash(f'Error al actualizar la contrata: {str(e)}', 'danger')
        return redirect(url_for('uc_contratas.contratas',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id
                                ))

def contratas_eliminar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id):
    '''
    Vista para eliminar una contrata
    '''
    try:
        # Eliminar la contrata
        delete = db.contratas.delete_one({
            '_id': ObjectId(contrata_id)
        })

        if delete.deleted_count > 0:
            flash('Contrata eliminada exitosamente', 'success')
            return redirect(url_for('uc_contratas.contratas',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id
                                ))
        else:
            flash('Error al eliminar la contrata', 'danger')
            return redirect(url_for('uc_contratas.contratas',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id
                                ))

    except Exception as e:
        flash(f'Error al eliminar la contrata: {str(e)}', 'danger')
        return redirect(url_for('uc_contratas.contratas',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                titular_id=titular_id
                                ))

def contratas_contrata_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, contrata_id):
    return render_template('usuarios_cogestores/contratas/index.html', 
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                           usuario_rol_gestor_id=usuario_rol_gestor_id, 
                           gestor_id=gestor_id, 
                           titular_id=titular_id, 
                           contrata_id=contrata_id
                           )

