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

def contratas_vista(gestor_id, titular_id):
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id)
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
            return redirect(url_for('ug_contratas.contratas', gestor_id=gestor_id, titular_id=titular_id))
        
        # Construir la consulta base - buscar contratas donde el titular_id sea el del titular actual
        consulta_filtros = {'titular_id': ObjectId(titular_id)}
        
        # Aplicar filtros si existen
        if filtrar_estado != 'todos':
            consulta_filtros['estado_contrata'] = filtrar_estado
        
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
                    filtrar_contrata.lower() not in contrata.get('telefono_contrata', '').lower() and
                    filtrar_contrata.lower() not in contrata.get('email_contrata', '').lower()):
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
                'email_contrata': contrata.get('email_contrata', ''),
                'estado_contrata': contrata.get('estado_contrata', contrata.get('estado', 'activo'))
            })

        return render_template('usuarios_gestores/contratas/listar.html',
                               contratas=contratas,
                               titular=titular,
                               nombre_gestor=nombre_gestor,
                               filtrar_contrata=filtrar_contrata,
                               filtrar_estado=filtrar_estado,
                               gestor_id=gestor_id
                               )
                             
    except Exception as e:
        flash(f'Error al cargar las contratas: {str(e)}', 'danger')
        return redirect(url_for('ug_titulares.titulares_titular', gestor_id=gestor_id, titular_id=titular_id))

def crear_contrata(gestor_id, titular_id, datos_formulario):
    """
    Crea una nueva contrata en la base de datos.
    
    Args:
        gestor_id (str): ID del gestor
        titular_id (str): ID del titular
        datos_formulario (dict): Datos del formulario
    
    Returns:
        tuple: (bool, dict) 
            - bool: True si se creó exitosamente, False si hubo error
            - dict: Datos del formulario o mensaje de error
    """
    try:
        # Obtener datos del formulario
        nombre_contrata = datos_formulario.get('nombre_contrata', '').strip().upper()
        cif_dni = datos_formulario.get('cif_dni', '').strip().upper()
        domicilio = datos_formulario.get('domicilio', '').strip()
        codigo_postal = datos_formulario.get('codigo_postal', '').strip()
        poblacion = datos_formulario.get('poblacion', '').strip().upper()
        provincia = datos_formulario.get('provincia', '').strip().upper()
        telefono_contrata = datos_formulario.get('telefono_contrata', '').strip()
        email_contrata = datos_formulario.get('email_contrata', '').strip().lower()
        
        # Verificar si ya existe una contrata con el mismo cif_dni para este titular
        contrata_existente = db.contratas.find_one({
            'titular_id': ObjectId(titular_id),
            'cif_dni': cif_dni
        })
        if contrata_existente:
            flash('Ya existe una contrata con este cif/dni para este titular', 'danger')
            return False, datos_formulario
            
        # Crear la contrata
        contrata = {
            'titular_id': ObjectId(titular_id),
            'nombre_contrata': nombre_contrata,
            'cif_dni': cif_dni,
            'domicilio': domicilio,
            'codigo_postal': codigo_postal,
            'poblacion': poblacion,
            'provincia': provincia,
            'telefono_contrata': telefono_contrata,
            'email_contrata': email_contrata,
            'estado_contrata': 'activo',
            'fecha_activacion': datetime.now(),
            'fecha_modificacion': datetime.now()
        }

        # Insertar la contrata
        insert = db.contratas.insert_one(contrata)
        if insert.inserted_id:
            flash('contrata creada correctamente', 'success')
            return True, None
        else:
            flash('Error al crear la contrata', 'danger')
            return False, datos_formulario

    except Exception as e:
        flash(f'Error al crear la contrata: {str(e)}', 'danger')
        return False, datos_formulario

def contratas_crear_vista(gestor_id, titular_id):

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
            return render_template('usuarios_gestores/contratas/crear.html',
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
            creado, datos_formulario = crear_contrata(gestor_id, titular_id, request.form)
            if creado:
                return redirect(url_for('ug_contratas.contratas', gestor_id=gestor_id, titular_id=titular_id))
            else:
                return render_template('usuarios_gestores/contratas/crear.html',
                                     gestor_id=gestor_id,
                                     titular_id=titular_id,
                                     usuario=usuario,
                                     usuario_rol_id=usuario_rol_id,
                                     gestor=gestor,
                                     titular=titular,
                                     nombre_gestor=nombre_gestor,
                                     datos_formulario=datos_formulario
                                     )

    except Exception as e:
        flash(f'Error al crear la contrata: {str(e)}', 'danger')
        return redirect(url_for('ug_contratas.contratas', gestor_id=gestor_id, titular_id=titular_id))

def actualizar_contrata(titular_id, contrata_id, datos_formulario):
    """
    Actualiza una contrata existente en la base de datos.
    
    Args:
        titular_id (str): ID del titular
        contrata_id (str): ID de la contrata a actualizar
        datos_formulario (dict): Datos del formulario
    
    Returns:
        tuple: (bool, dict) 
            - bool: True si se actualizó exitosamente, False si hubo error
            - dict: Datos del formulario o mensaje de error
    """
    try:
        # Obtener la contrata actual para comparar que no exista otra con el mismo cif/dni
        contrata_actual = db.contratas.find_one({'_id': ObjectId(contrata_id)})
        if not contrata_actual:
            flash('Contrata no encontrada', 'danger')
            return False, datos_formulario

        # Obtener datos del formulario
        nombre_contrata = datos_formulario.get('nombre_contrata', '').strip().upper()
        cif_dni = datos_formulario.get('cif_dni', '').strip().upper()
        domicilio = datos_formulario.get('domicilio', '').strip()
        codigo_postal = datos_formulario.get('codigo_postal', '').strip()
        poblacion = datos_formulario.get('poblacion', '').strip().upper()
        provincia = datos_formulario.get('provincia', '').strip().upper()
        telefono_contrata = datos_formulario.get('telefono_contrata', '').strip()
        email_contrata = datos_formulario.get('email_contrata', '').strip().lower()
        estado_contrata = datos_formulario.get('estado_contrata', '')

        # Verificar si el CIF/DNI ha cambiado
        if cif_dni != contrata_actual.get('cif_dni', ''):
            # Solo verificar duplicados si el CIF/DNI ha cambiado
            # Buscar si existe otra contrata con este CIF/DNI (excluyendo la actual)
            contrata_existente = db.contratas.find_one({
                'titular_id': ObjectId(titular_id),
                'cif_dni': cif_dni,
                '_id': {'$ne': ObjectId(contrata_id)}  # Excluir la contrata actual
            })
            if contrata_existente:
                flash('Ya existe otra contrata con este cif/dni para este titular', 'danger')
                return False, datos_formulario
        
        # Actualizar la contrata
        resultado = db.contratas.update_one(
            {'_id': ObjectId(contrata_id)},
            {
                '$set': {
                    'nombre_contrata': nombre_contrata,
                    'cif_dni': cif_dni,
                    'domicilio': domicilio,
                    'codigo_postal': codigo_postal,
                    'poblacion': poblacion,
                    'provincia': provincia,
                    'telefono_contrata': telefono_contrata,
                    'email_contrata': email_contrata,
                    'estado_contrata': estado_contrata,
                    'fecha_modificacion': datetime.now()
                }
            }
        )
        
        if resultado.modified_count > 0:
            flash('Contrata actualizada correctamente', 'success')
            return True, None
        else:
            flash('No se realizaron cambios en la contrata', 'info')
            return True, None

    except Exception as e:
        flash(f'Error al actualizar la contrata: {str(e)}', 'danger')
        return False, datos_formulario

def contratas_actualizar_vista(gestor_id, titular_id, contrata_id):
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id)
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_id, gestor, titular = resultado
        nombre_gestor = gestor.get('nombre_gestor', 'Gestor')
        
        # Convertir IDs a string para el template
        titular['_id'] = str(titular['_id'])
        
        # Obtener la contrata
        contrata = db.contratas.find_one({'_id': ObjectId(contrata_id)})
        if not contrata:
            flash('Contrata no encontrada', 'danger')
            return redirect(url_for('ug_contratas.contratas', gestor_id=gestor_id, titular_id=titular_id))
            
        # Convertir IDs a string para el template
        contrata['_id'] = str(contrata['_id'])
        contrata['titular_id'] = str(contrata['titular_id'])

        if request.method == 'GET':
            return render_template('usuarios_gestores/contratas/actualizar.html',
                                 gestor_id=gestor_id,
                                 titular_id=titular_id,
                                 usuario=usuario,
                                 usuario_rol_id=usuario_rol_id,
                                 gestor=gestor,
                                 titular=titular,
                                 nombre_gestor=nombre_gestor,
                                 contrata=contrata
                                 )

        if request.method == 'POST':
            # Procesar el formulario con la función actualizar_centro
            actualizado, datos_formulario = actualizar_contrata(titular_id, contrata_id, request.form)
            if actualizado:
                return redirect(url_for('ug_contratas.contratas', gestor_id=gestor_id, titular_id=titular_id))
            else:
                return render_template('usuarios_gestores/contratas/actualizar.html',
                                     gestor_id=gestor_id,
                                     titular_id=titular_id,
                                     usuario=usuario,
                                     usuario_rol_id=usuario_rol_id,
                                     gestor=gestor,
                                     titular=titular,
                                     nombre_gestor=nombre_gestor,
                                     contrata=contrata,
                                     datos_formulario=datos_formulario
                                     )

    except Exception as e:
        flash(f'Error al actualizar la contrata: {str(e)}', 'danger')
        return redirect(url_for('ug_contratas.contratas', gestor_id=gestor_id, titular_id=titular_id))

def eliminar_contrata(contrata_id):
    """
    Elimina una contrata de la base de datos.
    
    Args:
        contrata_id (str): ID de la contrata a eliminar
    
    Returns:
        bool: True si se eliminó exitosamente, False si hubo error
    """
    try:
        # Verificar si el centro existe
        contrata = db.contratas.find_one({'_id': ObjectId(contrata_id)})
        if not contrata:
            flash('Contrata no encontrada', 'danger')
            return False
            
        # Eliminar la contrata
        delete = db.contratas.delete_one({'_id': ObjectId(contrata_id)})
        if delete.deleted_count > 0:
            flash('Contrata eliminada correctamente', 'success')
            return True
        else:
            flash('Error al eliminar la contrata', 'danger')
            return False

    except Exception as e:
        flash(f'Error al eliminar la contrata: {str(e)}', 'danger')
        return False

def contratas_eliminar_vista(gestor_id, titular_id, contrata_id):
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id)
        if not permisos_ok:
            return resultado
            
        # Ejecutar la eliminación
        eliminado = eliminar_contrata(contrata_id)
        if eliminado:
            return redirect(url_for('ug_contratas.contratas', gestor_id=gestor_id, titular_id=titular_id))
        else:
            return redirect(url_for('ug_contratas.contratas', gestor_id=gestor_id, titular_id=titular_id))

    except Exception as e:
        flash(f'Error al eliminar la contrata: {str(e)}', 'danger')
        return redirect(url_for('ug_contratas.contratas', gestor_id=gestor_id, titular_id=titular_id))

def contratas_contrata_vista(gestor_id, titular_id, contrata_id):
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id)
        if not permisos_ok:
            return resultado
        
        # Verificar que la contratata pertenece al titular actual
        contrata = db.contratas.find_one({
            '_id': ObjectId(contrata_id),
            'titular_id': ObjectId(titular_id)
        })
        if not contrata:
            flash('Contrata no encontrada o no pertenece a este titular', 'danger')
            return redirect(url_for('ug_contratas.contratas', gestor_id=gestor_id, titular_id=titular_id))
        
        return render_template('usuarios_gestores/contratas/index.html',
                               contrata=contrata,
                               gestor_id=gestor_id,
                               titular_id=titular_id)
    except Exception as e:
        flash(f'Error al cargar la contratata: {str(e)}', 'danger')
        return redirect(url_for('ug_contratas.contratas', gestor_id=gestor_id, titular_id=titular_id))

