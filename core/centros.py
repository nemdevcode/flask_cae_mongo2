from flask import render_template, session, request, redirect, url_for, flash, jsonify
from bson.objectid import ObjectId

from datetime import datetime

from config import conexion_mongo

db = conexion_mongo()

def obtener_titulares_activos(gestor_id):

    """Obtiene los titulares activos para un gestor específico"""
    titulares = list(db.usuarios.aggregate([
        {
            "$match": {
                "_id": {"$in": [ObjectId(rel['usuario_id']) for rel in db.usuarios_titulares.find({"gestor_id": ObjectId(gestor_id), "estado": "activo"})]}
            }
        },
        {
            "$lookup": {
                "from": "usuarios_titulares",
                "localField": "_id",
                "foreignField": "usuario_id",
                "as": "titular_info"
            }
        },
        {
            "$unwind": {
                "path": "$titular_info",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$match": {
                "titular_info.gestor_id": ObjectId(gestor_id),
                "titular_info.estado": "activo"
            }
        },
        {
            "$project": {
                "_id": 1,
                "nombre": "$nombre_usuario",
                "alias": "$titular_info.alias"
            }
        },
        {
            "$sort": {
                "alias": 1
            }
        }
    ]))
    
    # Convertir ObjectId a string para cada titular
    for titular in titulares:
        titular['_id'] = str(titular['_id'])
    
    return titulares

def obtener_centros(titular_id):
    
    """Obtiene los centros activos para un titular específico"""
    centros = list(db.centros.find({"titular_id": ObjectId(titular_id)}))
    # Convertir ObjectId a string para cada centro
    for centro in centros:
        centro['_id'] = str(centro['_id'])
        centro['titular_id'] = str(centro['titular_id'])
    return centros

def gestores_centros_vista():
    
    try:
        # Obtener el ID del gestor actual
        gestor_id = session.get('usuario_id')
        if not gestor_id:
            return redirect(url_for('login', mensaje_error='No hay gestor autenticado'))

        # Obtener el nombre del gestor
        gestor = db.usuarios.find_one({'_id': ObjectId(gestor_id)})
        nombre_gestor = gestor.get('nombre_usuario', '') if gestor else ''

        # Obtener el ID del titular a expandir
        expandir_titular = request.form.get('expandir_titular') or request.args.get('expandir_titular')

        # Obtener el filtro de titular
        filtro_titular = request.form.get('filtrar_titular', '').strip().upper()

        # Obtener titulares activos
        titulares = obtener_titulares_activos(gestor_id)

        # Filtrar titulares si hay un filtro
        if filtro_titular:
            titulares = [
                titular for titular in titulares
                if filtro_titular in titular['alias'].upper() or 
                   filtro_titular in titular['nombre'].upper()
            ]

        # Obtener centros para cada titular
        centros_por_titular = {}
        for titular in titulares:
            # Obtener filtros específicos para este titular
            filtro_centro = request.form.get(f'filtrar_centro_{titular["_id"]}', '').strip().upper()
            filtro_estado = request.form.get(f'filtrar_estado_{titular["_id"]}', 'todos')

            # Obtener y filtrar centros
            centros = obtener_centros(titular['_id'])
            
            # Aplicar filtro de texto si existe
            if filtro_centro:
                centros = [
                    centro for centro in centros
                    if (filtro_centro in centro['nombre_centro'].upper() or
                        filtro_centro in centro['domicilio'].upper() or
                        filtro_centro in centro['codigo_postal'].upper() or
                        filtro_centro in centro['poblacion'].upper() or
                        filtro_centro in centro['provincia'].upper())
                ]

            # Aplicar filtro de estado si no es 'todos'
            if filtro_estado != 'todos':
                centros = [centro for centro in centros if centro['estado'] == filtro_estado]

            centros_por_titular[titular['_id']] = centros

        # Obtener mensajes de la URL
        mensaje_ok = request.args.get('mensaje_ok', '')
        mensaje_error = request.args.get('mensaje_error', '')

        return render_template('gestores/centros/listar.html',
                             nombre_gestor=nombre_gestor,
                             titulares=titulares,
                             centros_por_titular=centros_por_titular,
                             expandir_titular=expandir_titular,
                             mensaje_ok=mensaje_ok,
                             mensaje_error=mensaje_error)
                             
    except Exception as e:
        return redirect(url_for('gestores.gestores_centros', 
                              mensaje_error=f'Error al cargar los centros: {str(e)}'))

def gestores_centros_crear_vista():
    
    try:
        # Obtener el ID del gestor actual
        gestor_id = session.get('usuario_id')
        print(f"Gestor ID: {gestor_id}")
        if not gestor_id:
            return redirect(url_for('login', mensaje_error='No hay gestor autenticado'))

        # Obtener el ID del titular (de GET o POST según el método)
        if request.method == 'GET':
            titular_id = request.args.get('titular_id')
        else:
            titular_id = request.form.get('titular_id')
            
        print(f"Titular ID recibido: {titular_id}")
        if not titular_id:
            return redirect(url_for('gestores.gestores_centros', 
                                  mensaje_error='ID de titular no proporcionado'))

        # Verificar que el titular pertenece al gestor actual
        print(f"Buscando titular con ID: {titular_id} y gestor_id: {gestor_id}")
        # Primero buscamos el titular en la colección usuarios_titulares
        titular = db.usuarios_titulares.find_one({
            'usuario_id': ObjectId(titular_id),
            'gestor_id': ObjectId(gestor_id)
        })
        print(f"Titular encontrado: {titular}")
        if not titular:
            return redirect(url_for('gestores.gestores_centros', 
                                  mensaje_error='Titular no encontrado o no pertenece a este gestor'))

        # Obtener la información del titular
        titular_info = db.usuarios.find_one({'_id': titular['usuario_id']})
        print(f"Titular info encontrada: {titular_info}")
        if not titular_info:
            return redirect(url_for('gestores.gestores_centros', 
                                  mensaje_error='Titular no encontrado'))

        if request.method == 'GET':
            return render_template('gestores/centros/crear.html',
                                 titular_id=titular_id,
                                 titular_info={
                                     'alias': titular['alias'],
                                     'nombre': titular_info['nombre_usuario']
                                 })

        if request.method == 'POST':
            # Obtener datos del formulario
            nombre_centro = request.form.get('nombre_centro', '').strip().upper()
            domicilio = request.form.get('domicilio', '').strip().upper()
            codigo_postal = request.form.get('codigo_postal', '').strip().upper()
            poblacion = request.form.get('poblacion', '').strip().upper()
            provincia = request.form.get('provincia', '').strip().upper()

            # Verificar si ya existe un centro con el mismo nombre para este titular
            if db.centros.find_one({
                'nombre_centro': nombre_centro,
                'titular_id': ObjectId(titular_id)
            }):
                return render_template('gestores/centros/crear.html',
                                    titular_id=titular_id,
                                    titular_info={
                                        'alias': titular['alias'],
                                        'nombre': titular_info['nombre_usuario']
                                    },
                                    mensaje_error='Ya existe un centro con este nombre para este titular',
                                    form_data=request.form)

            # Crear el centro
            centro_data = {
                'titular_id': ObjectId(titular_id),
                'nombre_centro': nombre_centro,
                'domicilio': domicilio,
                'codigo_postal': codigo_postal,
                'poblacion': poblacion,
                'provincia': provincia,
                'estado': 'activo',  # Siempre se crea como activo
                'fecha_alta': datetime.now(),
                'fecha_modificacion': datetime.now(),
                'fecha_baja': None
            }
            
            db.centros.insert_one(centro_data)
            
            return redirect(url_for('gestores.gestores_centros', 
                                  mensaje_ok='Centro creado exitosamente',
                                  expandir_titular=titular_id))

    except Exception as e:
        print(f"Error en gestores_centros_crear_vista: {str(e)}")
        return render_template('gestores/centros/crear.html',
                             titular_id=titular_id if 'titular_id' in locals() else None,
                             titular_info=titular_info if 'titular_info' in locals() else None,
                             mensaje_error=f'Error al crear el centro: {str(e)}',
                             form_data=request.form if request.method == 'POST' else None)

def gestores_centros_actualizar_vista():
    
    try:
        # Obtener el ID del gestor actual
        gestor_id = session.get('usuario_id')
        if not gestor_id:
            return redirect(url_for('login', mensaje_error='No hay gestor autenticado'))

        # Obtener el ID del centro a actualizar
        centro_id = request.args.get('centro_id')
        if not centro_id:
            return redirect(url_for('gestores.gestores_centros', 
                                  mensaje_error='ID de centro no proporcionado'))

        # Obtener el ID del titular a expandir (tanto de GET como de POST)
        expandir_titular = request.args.get('expandir_titular') or request.form.get('expandir_titular')

        # Obtener el centro y verificar que pertenece a un titular del gestor actual
        centro = db.centros.find_one({'_id': ObjectId(centro_id)})
        if not centro:
            return redirect(url_for('gestores.gestores_centros', 
                                  mensaje_error='Centro no encontrado'))

        # Verificar que el titular del centro pertenece al gestor actual
        titular = db.usuarios_titulares.find_one({
            'usuario_id': centro['titular_id'],
            'gestor_id': ObjectId(gestor_id)
        })

        if not titular:
            return redirect(url_for('gestores.gestores_centros', 
                                  mensaje_error='Centro no pertenece a un titular de este gestor'))

        # Obtener la información del titular
        titular_info = db.usuarios.find_one({'_id': titular['usuario_id']})
        if not titular_info:
            return redirect(url_for('gestores.gestores_centros', 
                                  mensaje_error='Titular no encontrado'))

        # Preparar los datos para el template
        centro_data = {
            '_id': centro['_id'],
            'nombre_centro': centro['nombre_centro'],
            'domicilio': centro['domicilio'],
            'codigo_postal': centro['codigo_postal'],
            'poblacion': centro['poblacion'],
            'provincia': centro['provincia'],
            'estado': centro['estado'],
            'titular_id': str(titular['_id']),
            'titular_info': {
                'alias': titular['alias'],
                'nombre': titular_info['nombre_usuario']
            }
        }

        if request.method == 'GET':
            return render_template('gestores/centros/actualizar.html', 
                                 centro=centro_data,
                                 expandir_titular=expandir_titular)

        if request.method == 'POST':
            # Obtener datos del formulario
            nombre_centro = request.form.get('nombre_centro', '').strip().upper()
            domicilio = request.form.get('domicilio', '').strip().upper()
            codigo_postal = request.form.get('codigo_postal', '').strip().upper()
            poblacion = request.form.get('poblacion', '').strip().upper()
            provincia = request.form.get('provincia', '').strip().upper()
            estado = request.form.get('estado', 'activo')

            # Verificar si ya existe un centro con el mismo nombre para este titular
            if db.centros.find_one({
                'nombre_centro': nombre_centro,
                'titular_id': centro['titular_id'],
                '_id': {'$ne': ObjectId(centro_id)}
            }):
                return render_template('gestores/centros/actualizar.html',
                                    centro=centro_data,
                                    expandir_titular=expandir_titular,
                                    mensaje_error='Ya existe un centro con este nombre para este titular')

            # Actualizar el centro
            db.centros.update_one(
                {'_id': ObjectId(centro_id)},
                {
                    '$set': {
                        'nombre_centro': nombre_centro,
                        'domicilio': domicilio,
                        'codigo_postal': codigo_postal,
                        'poblacion': poblacion,
                        'provincia': provincia,
                        'estado': estado,
                        'fecha_modificacion': datetime.now()
                    }
                }
            )

            return redirect(url_for('gestores.gestores_centros', 
                                  mensaje_ok='Centro actualizado exitosamente',
                                  expandir_titular=expandir_titular))

    except Exception as e:
        return render_template('gestores/centros/actualizar.html',
                             centro=centro_data if 'centro_data' in locals() else None,
                             expandir_titular=expandir_titular if 'expandir_titular' in locals() else None,
                             mensaje_error=f'Error al actualizar el centro: {str(e)}')

def gestores_centros_eliminar_vista():
    
    """Elimina un centro de un titular del gestor actual"""
    try:
        # Obtener el ID del gestor actual
        gestor_id = session.get('usuario_id')
        if not gestor_id:
            return redirect(url_for('login', mensaje_error='No hay gestor autenticado'))

        # Obtener el ID del centro a eliminar
        centro_id = request.args.get('centro_id')
        if not centro_id:
            return redirect(url_for('gestores.gestores_centros', 
                                  mensaje_error='ID de centro no proporcionado'))

        # Obtener el centro y verificar que pertenece a un titular del gestor actual
        centro = db.centros.find_one({'_id': ObjectId(centro_id)})
        if not centro:
            return redirect(url_for('gestores.gestores_centros', 
                                  mensaje_error='Centro no encontrado'))

        # Verificar que el titular del centro pertenece al gestor actual
        titular = db.usuarios_titulares.find_one({
            'usuario_id': centro['titular_id'],
            'gestor_id': ObjectId(gestor_id)
        })

        if not titular:
            return redirect(url_for('gestores.gestores_centros', 
                                  mensaje_error='Centro no pertenece a un titular de este gestor'))

        # Eliminar el centro
        db.centros.delete_one({'_id': ObjectId(centro_id)})
        
        # Redirigir de vuelta a la vista de centros con mensaje de éxito
        return redirect(url_for('gestores.gestores_centros', mensaje_ok='Centro eliminado correctamente', expandir_titular=request.args.get('expandir_titular')))
        
    except Exception as e:
        # En caso de error, redirigir con mensaje de error
        return redirect(url_for('gestores.gestores_centros', mensaje_error=str(e), expandir_titular=request.args.get('expandir_titular')))