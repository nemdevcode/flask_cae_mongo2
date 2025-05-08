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
        
        # Construir la consulta base - buscar requeerimientos del gestor
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

                requerimientos.append(
                    {
                    '_id': str(requerimiento['_id']),
                    'referencia_requerimiento': requerimiento['referencia_requerimiento'],
                    'nombre_requerimiento': requerimiento['nombre_requerimiento'],
                    'estado_requerimiento': requerimiento['estado_requerimiento']
                }
            )
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
    
def crear_requerimiento(gestor_id):
    '''
    Función para crear un nuevo requerimiento.
    '''
    pass

def requerimientos_crear_vista(gestor_id):
    '''
    Vista de usuarios de gestores para crear un nuevo requerimiento.
    '''
    return render_template('usuarios_gestores/requerimientos/crear.html', gestor_id=gestor_id)

def actualizar_requerimiento(gestor_id, requerimiento_id):
    '''
    Función para actualizar un requerimiento.
    '''
    pass

def requerimientos_actualizar_vista(gestor_id, requerimiento_id):
    '''
    Vista de usuarios de gestores para actualizar un requerimiento.
    '''
    return render_template('usuarios_gestores/requerimientos/actualizar.html', gestor_id=gestor_id, requerimiento_id=requerimiento_id)

def requerimientos_eliminar_vista(gestor_id, requerimiento_id):
    '''
    Vista de usuarios de gestores para eliminar un requerimiento.
    '''
    return render_template('usuarios_gestores/requerimientos/eliminar.html', gestor_id=gestor_id, requerimiento_id=requerimiento_id)


