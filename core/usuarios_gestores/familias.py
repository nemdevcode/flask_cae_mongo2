from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from datetime import datetime
from config import conexion_mongo
from models.familias_model import FamiliasCollection

db = conexion_mongo()

def familias_vista(gestor_id, titular_id):
    '''
    Vista para listar las familias de un titular
    '''
    try:
        # Obtener nombre del titular
        nombre_titular = db.titulares.find_one({'_id': ObjectId(titular_id)})['nombre_titular']

        # Obtener parámetros de filtrado
        filtrar_familia = request.form.get('filtrar_familia', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos_estados')
        filtrar_tipo = request.form.get('filtrar_tipo', 'todos_tipos')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('ug_familias.familias', 
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id))
        
        # Construir la consulta base - buscar familias del titular
        consulta_filtros = {'titular_id': ObjectId(titular_id)}

        # Aplicar filtros si existen
        if filtrar_estado != 'todos_estados':
            consulta_filtros['estado_familia'] = filtrar_estado
        
        if filtrar_tipo != 'todos_tipos':
            consulta_filtros['tipo_familia'] = filtrar_tipo

        # Obtener las familias del titular
        familias = []
        familias_titular = db.familias.find(consulta_filtros)

        for familia in familias_titular:
            # Si hay filtro por texto, verificar si coincide en algún campo
            if filtrar_familia:
                if (filtrar_familia.lower() not in familia['nombre_familia'].lower()):
                    continue
            
            familias.append(
                {
                    '_id': str(familia['_id']),
                    'nombre_familia': familia['nombre_familia'],
                    'tipo_familia': familia['tipo_familia'],
                    'estado_familia': familia['estado_familia']
                }
            )

        return render_template('usuarios_gestores/familias/listar.html', 
                               gestor_id=gestor_id,
                               titular_id=titular_id,
                               nombre_titular=nombre_titular,
                               familias=familias,
                               filtrar_familia=filtrar_familia,
                               filtrar_estado=filtrar_estado,
                               filtrar_tipo=filtrar_tipo)
    except Exception as e:
        flash(f'Error al listar las familias: {e}', 'danger')
        return redirect(url_for('ug_titulares.titulares_titular', 
                               gestor_id=gestor_id,
                               titular_id=titular_id))

def crear_familia(titular_id, datos_formulario):
    '''
    Vista para crear una familia
    '''
    try:
        # Obtener los datos del formulario
        referencia_familia = datos_formulario.get('referencia_familia')
        nombre_familia = datos_formulario.get('nombre_familia')
        tipo_familia = datos_formulario.get('tipo_familia')
        descripcion_familia = datos_formulario.get('descripcion_familia')
        notas_familia = datos_formulario.get('notas_familia')

        # Crear la familia
        familia = FamiliasCollection(
            titular_id=ObjectId(titular_id),
            referencia_familia=referencia_familia,
            nombre_familia=nombre_familia,
            tipo_familia=tipo_familia,
            estado_familia='activo',
            fecha_creacion=datetime.now(),
            fecha_modificacion=datetime.now(),
            fecha_inactivacion=None,
            descripcion_familia=descripcion_familia,
            notas_familia=notas_familia
        )

        # Insertar
        insert = db.familias.insert_one(familia.to_dict())

        if insert.inserted_id:
            flash('Familia creada correctamente', 'success')
            return True, None
        else:
            flash('Error al crear la familia', 'danger')
            return False, datos_formulario

    except Exception as e:
        flash(f'Error al procesar el formulario: {str(e)}', 'danger')
        return False, datos_formulario

def familias_crear_vista(gestor_id, titular_id):
    '''
    Vista para crear una familia
    '''
    try:
        # Si es una petición POST, procesar el formulario
        if request.method == 'POST':
            creado, datos_formulario = crear_familia(titular_id, request.form)
            if creado:
                return redirect(url_for('ug_familias.familias', 
                           gestor_id=gestor_id, 
                           titular_id=titular_id))
            else:
                return render_template('usuarios_gestores/familias/crear.html', 
                                       gestor_id=gestor_id, 
                                       titular_id=titular_id, 
                                       datos_formulario=datos_formulario)
            
        # Si es una petición GET, mostrar el formulario vacío
        return render_template('usuarios_gestores/familias/crear.html', 
                               gestor_id=gestor_id, 
                               titular_id=titular_id)

    except Exception as e:
        flash(f'Error al procesar el formulario: {str(e)}', 'danger')
        return redirect(url_for('ug_familias.familias_crear_vista', 
                               gestor_id=gestor_id, 
                               titular_id=titular_id))

def actualizar_familia(familia_id, datos_formulario):
    '''
    Vista para actualizar una familia
    '''
    try:
        # Obtener los datos del formulario
        referencia_familia = datos_formulario.get('referencia_familia')
        nombre_familia = datos_formulario.get('nombre_familia')
        tipo_familia = datos_formulario.get('tipo_familia')
        estado_familia = datos_formulario.get('estado_familia')
        descripcion_familia = datos_formulario.get('descripcion_familia')
        notas_familia = datos_formulario.get('notas_familia')

        # Actualizar la familia
        update = db.familias.update_one({
            '_id': ObjectId(familia_id)
        }, {
            '$set': {
                'referencia_familia': referencia_familia,
                'nombre_familia': nombre_familia,
                'tipo_familia': tipo_familia,
                'estado_familia': estado_familia,
                'fecha_modificacion': datetime.now(),
                'fecha_inactivacion': None,
                'descripcion_familia': descripcion_familia,
                'notas_familia': notas_familia
            }
        })

        if update.modified_count > 0:
            flash('Familia actualizada correctamente', 'success')
            return True, None
        else:
            flash('Error al actualizar la familia', 'danger')
            return False, datos_formulario
        
    except Exception as e:
        flash(f'Error al actualizar la familia: {e}', 'danger')
        return False, datos_formulario

def familias_actualizar_vista(gestor_id, titular_id, familia_id):
    '''
    Vista para actualizar una familia
    '''
    try:
        # Obtener la familia a actualizar
        familia = db.familias.find_one({
            '_id': ObjectId(familia_id)
        })

        if request.method == 'POST':
            actualizado, datos_formulario = actualizar_familia(familia_id, request.form)
            if actualizado:
                return redirect(url_for('ug_familias.familias', 
                                        gestor_id=gestor_id, 
                                        titular_id=titular_id))
            else:
                return render_template('usuarios_gestores/familias/actualizar.html', 
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id, 
                                    familia=familia, 
                                    datos_formulario=datos_formulario)
        
        return render_template('usuarios_gestores/familias/actualizar.html', 
                                gestor_id=gestor_id, 
                                titular_id=titular_id, 
                                familia=familia)

    except Exception as e:
        flash(f'Error al actualizar la familia: {e}', 'danger')
        return redirect(url_for('ug_familias.familias', 
                               gestor_id=gestor_id, 
                               titular_id=titular_id))

def familias_eliminar_vista(gestor_id, titular_id, familia_id):
    '''
    Vista para eliminar una familia
    '''
    try:
        # Eliminar la familia
        delete = db.familias.delete_one({
            '_id': ObjectId(familia_id)
        })

        if delete.deleted_count > 0:
            flash('Familia eliminada correctamente', 'success')
            return redirect(url_for('ug_familias.familias',
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id))
        else:
            flash('Error al eliminar la familia', 'danger')
            return redirect(url_for('ug_familias.familias_eliminar_vista',
                                    gestor_id=gestor_id, 
                                    titular_id=titular_id, 
                                    familia_id=familia_id))

    except Exception as e:
        flash(f'Error al eliminar la familia: {e}', 'danger')
        return redirect(url_for('ug_familias.familias', 
                               gestor_id=gestor_id, 
                               titular_id=titular_id))

def familias_familia_vista(gestor_id, titular_id, familia_id):
    '''
    Vista para mostrar una familia y añadir requerimientos a la familia
    '''
    return render_template('usuarios_gestores/familias/index.html', 
                           gestor_id=gestor_id, 
                           titular_id=titular_id, 
                           familia_id=familia_id)
