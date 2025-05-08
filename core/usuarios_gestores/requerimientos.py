from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from datetime import datetime
from config import conexion_mongo
from models.requerimientos_model import RequerimientosCollection

db = conexion_mongo()

def requerimientos_vista(gestor_id):
    '''
    Vista de usuarios de gestores para gestionar requerimientos.
    '''
    try:
        # Obtener nombre del gestor
        nombre_gestor = db.gestores.find_one({'_id': ObjectId(gestor_id)})['nombre_gestor']

        # Obtener parámetros de filtrado
        filtrar_requerimiento = request.form.get('filtrar_requerimiento', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')
        
        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('ug_requerimientos.requerimientos', 
                                    gestor_id=gestor_id
                                    ))
        
        # Construir la consulta base - buscar requerimientos del gestor
        consulta_filtros = {'gestor_id': ObjectId(gestor_id)}

        # Aplicar filtros si existen
        if filtrar_estado != 'todos':
            consulta_filtros['estado_requerimiento'] = filtrar_estado
        
        # Obtener los requerimientos del gestor
        requerimientos = []
        requerimientos_gestor = db.requerimientos.find(consulta_filtros)

        for requerimiento in requerimientos_gestor:
            # Si hay filtro por texto, verificar si coincide en algún campo
            if filtrar_requerimiento:
                if (filtrar_requerimiento.lower() not in requerimiento['referencia_requerimiento'].lower() and
                    filtrar_requerimiento.lower() not in requerimiento['nombre_requerimiento'].lower()):
                    continue
            
            requerimientos.append({
                '_id': str(requerimiento['_id']),
                'referencia_requerimiento': requerimiento['referencia_requerimiento'],
                'nombre_requerimiento': requerimiento['nombre_requerimiento'],
                'estado_requerimiento': requerimiento['estado_requerimiento']
            })

        return render_template('usuarios_gestores/requerimientos/listar.html',
                               gestor_id=gestor_id,
                               nombre_gestor=nombre_gestor,
                               requerimientos=requerimientos,
                               filtrar_requerimiento=filtrar_requerimiento,
                               filtrar_estado=filtrar_estado)
    
    except Exception as e:
        flash(f'Error al cargar la vista de requerimientos: {str(e)}', 'danger')
        return redirect(url_for('ug_requerimientos.requerimientos',
                                gestor_id=gestor_id))
    
def crear_requerimiento(gestor_id, datos_formulario):
    '''
    Función para crear un nuevo requerimiento.
    '''
    try:
        # Obtener los datos del formulario
        referencia_requerimiento = datos_formulario.get('referencia_requerimiento')
        nombre_requerimiento = datos_formulario.get('nombre_requerimiento')
        descripcion_requerimiento = datos_formulario.get('descripcion_requerimiento')
        notas_requerimiento = datos_formulario.get('notas_requerimiento')

        # Crear un nuevo requerimiento
        nuevo_requerimiento = RequerimientosCollection(
            gestor_id=ObjectId(gestor_id),
            referencia_requerimiento=referencia_requerimiento,
            nombre_requerimiento=nombre_requerimiento,
            estado_requerimiento='activo',
            fecha_activacion=datetime.now(),
            fecha_modificacion=datetime.now(),
            fecha_inactivacion=None,
            descripcion_requerimiento=descripcion_requerimiento,
            notas_requerimiento=notas_requerimiento
        )
        
        # Insertar el nuevo requerimiento en la base de datos
        insert = db.requerimientos.insert_one(nuevo_requerimiento.to_dict())

        if insert.inserted_id:
            flash('Requerimiento creado correctamente', 'success')
            return True, None
        else:
            flash('Error al crear el requerimiento', 'danger')
            return False, datos_formulario
            
    except Exception as e:
        flash(f'Error al procesar el formulario: {str(e)}', 'danger')
        return False, datos_formulario

def requerimientos_crear_vista(gestor_id):
    '''
    Vista de usuarios de gestores para crear un nuevo requerimiento.
    '''
    try:
        # Si es una petición POST, procesar el formulario
        if request.method == 'POST':
            creado, datos_formulario = crear_requerimiento(gestor_id, request.form)
            if creado:
                return redirect(url_for('ug_requerimientos.requerimientos', 
                                        gestor_id=gestor_id))
            else:
                return render_template('usuarios_gestores/requerimientos/crear.html', 
                                        gestor_id=gestor_id, 
                                        datos_formulario=datos_formulario)
        
        # Si es una petición GET, mostrar el formulario vacío
        return render_template('usuarios_gestores/requerimientos/crear.html', 
                                gestor_id=gestor_id)

    except Exception as e:
        flash(f'Error al procesar el formulario: {str(e)}', 'danger')
        return redirect(url_for('ug_requerimientos.requerimientos_crear', 
                                gestor_id=gestor_id))

def actualizar_requerimiento(requerimiento_id, datos_formulario):
    '''
    Función para actualizar un requerimiento.
    '''
    try:
        # Obtener los datos del formulario
        referencia_requerimiento = datos_formulario.get('referencia_requerimiento')
        nombre_requerimiento = datos_formulario.get('nombre_requerimiento')
        estado_requerimiento = datos_formulario.get('estado_requerimiento')
        descripcion_requerimiento = datos_formulario.get('descripcion_requerimiento')
        notas_requerimiento = datos_formulario.get('notas_requerimiento')
        # Obtener el requerimiento actual
        requerimiento_actual = db.requerimientos.find_one({'_id': ObjectId(requerimiento_id)})

        # Actualizar el requerimiento en la base de datos
        update = db.requerimientos.update_one({
            '_id': ObjectId(requerimiento_id)
        }, {
            '$set': {
                'referencia_requerimiento': referencia_requerimiento,
                'nombre_requerimiento': nombre_requerimiento,
                'estado_requerimiento': estado_requerimiento,
                'fecha_modificacion': datetime.now(),
                'fecha_inactivacion': None,
                'descripcion_requerimiento': descripcion_requerimiento,
                'notas_requerimiento': notas_requerimiento
            }
        })

        if update.modified_count > 0:
            flash('Requerimiento actualizado correctamente', 'success')
            return True, None
        else:
            flash('Error al actualizar el requerimiento', 'danger')
            return False, datos_formulario
        
    except Exception as e:
        flash(f'Error al actualizar el requerimiento: {str(e)}', 'danger')
        return False, datos_formulario

def requerimientos_actualizar_vista(gestor_id, requerimiento_id):
    '''
    Vista de usuarios de gestores para actualizar un requerimiento.
    '''
    try:
        # Obtener el requerimiento a actualizar
        requerimiento = db.requerimientos.find_one({
            '_id': ObjectId(requerimiento_id)
        })
        
        if request.method == 'POST':
            actualizado, datos_formulario = actualizar_requerimiento(requerimiento_id, request.form)
            if actualizado:
                return redirect(url_for('ug_requerimientos.requerimientos', 
                                        gestor_id=gestor_id))
            else:
                return render_template('usuarios_gestores/requerimientos/actualizar.html', 
                                        gestor_id=gestor_id, 
                                        requerimiento=requerimiento, 
                                        datos_formulario=datos_formulario)
            
        return render_template('usuarios_gestores/requerimientos/actualizar.html', 
                                gestor_id=gestor_id, 
                                requerimiento=requerimiento)

    except Exception as e:
        flash(f'Error al actualizar el requerimiento: {str(e)}', 'danger')
        return redirect(url_for('ug_requerimientos.requerimientos_actualizar', 
                                gestor_id=gestor_id, 
                                requerimiento_id=requerimiento_id))

def requerimientos_eliminar_vista(gestor_id, requerimiento_id):
    '''
    Vista de usuarios de gestores para eliminar un requerimiento.
    '''
    return render_template('usuarios_gestores/requerimientos/eliminar.html', gestor_id=gestor_id, requerimiento_id=requerimiento_id)


