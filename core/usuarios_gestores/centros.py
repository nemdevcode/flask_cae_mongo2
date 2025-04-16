from flask import render_template, session, request, redirect, url_for, flash, jsonify
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
    print(f"gestor_id: {gestor_id}, titular_id: {titular_id}")

    gestor_id = ObjectId(gestor_id)
    titular_id = ObjectId(titular_id)

    print(f"gestor_id: {gestor_id}, titular_id: {titular_id}")
    
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id)
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_id, gestor, titular = resultado
        nombre_gestor = gestor.get('nombre_gestor', 'Gestor')
        
        # Obtener los centros del titular
        filtros = {'titular_id': titular_id}
        
        # Aplicar filtros adicionales si existen en el formulario
        if request.method == 'POST':
            filtro_centro = request.form.get(f'filtrar_centro_{titular_id}', '').strip()
            filtro_estado = request.form.get(f'filtrar_estado_{titular_id}', 'todos')
            
            # Filtro de texto (buscar en varios campos)
            if filtro_centro:
                filtros['$or'] = [
                    {'nombre_centro': {'$regex': filtro_centro, '$options': 'i'}},
                    {'domicilio': {'$regex': filtro_centro, '$options': 'i'}},
                    {'codigo_postal': {'$regex': filtro_centro, '$options': 'i'}},
                    {'poblacion': {'$regex': filtro_centro, '$options': 'i'}},
                    {'provincia': {'$regex': filtro_centro, '$options': 'i'}}
                ]
            
            # Filtro por estado
            if filtro_estado != 'todos':
                filtros['estado'] = filtro_estado
        
        # Ejecutar la consulta para obtener los centros
        centros = list(db.centros.find(filtros))
        
        # Convertir ObjectId a string para usar en el template
        for centro in centros:
            centro['_id'] = str(centro['_id'])
            centro['titular_id'] = str(centro['titular_id'])

        # Convertir los ObjectId a string para usar en el template
        gestor_id = str(gestor_id)
        titular_id = str(titular_id)
        titular['_id'] = str(titular['_id'])

        return render_template('usuarios_gestores/centros/listar.html',
                               gestor_id=gestor_id,
                               titular_id=titular_id,
                               usuario=usuario,
                               usuario_rol_id=usuario_rol_id,
                               gestor=gestor,
                               titular=titular,
                               nombre_gestor=nombre_gestor,
                               centros=centros
                               )
                             
    except Exception as e:
        flash(f'Error al cargar los centros: {str(e)}', 'danger')
        return redirect(url_for('ug_titulares.titulares_titular', gestor_id=gestor_id, titular_id=titular_id))

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
            # Obtener datos del formulario
            nombre_centro = request.form.get('nombre_centro', '').strip().upper()
            domicilio = request.form.get('domicilio', '').strip().upper()
            codigo_postal = request.form.get('codigo_postal', '').strip().upper()
            poblacion = request.form.get('poblacion', '').strip().upper()
            provincia = request.form.get('provincia', '').strip().upper()

            # Validar datos
            if not all([nombre_centro, domicilio, codigo_postal, poblacion, provincia]):
                flash('Todos los campos son obligatorios', 'danger')
                return render_template('usuarios_gestores/centros/crear.html',
                                     gestor_id=gestor_id,
                                     titular_id=titular_id,
                                     usuario=usuario,
                                     usuario_rol_id=usuario_rol_id,
                                     gestor=gestor,
                                     titular=titular,
                                     nombre_gestor=nombre_gestor,
                                     form_data=request.form)

            # Crear el centro
            centro = {
                'nombre_centro': nombre_centro,
                'domicilio': domicilio,
                'codigo_postal': codigo_postal,
                'poblacion': poblacion,
                'provincia': provincia,
                'titular_id': ObjectId(titular_id),
                'estado': 'activo',
                'fecha_creacion': datetime.now(),
                'fecha_actualizacion': datetime.now()
            }

            # Insertar el centro
            resultado = db.centros.insert_one(centro)
            if resultado.inserted_id:
                flash('Centro creado correctamente', 'success')
                return redirect(url_for('ug_centros.centros', gestor_id=gestor_id, titular_id=titular_id))
            else:
                flash('Error al crear el centro', 'danger')
                return redirect(url_for('ug_centros.centros', gestor_id=gestor_id, titular_id=titular_id))

    except Exception as e:
        flash(f'Error al crear el centro: {str(e)}', 'danger')
        return redirect(url_for('ug_centros.centros', gestor_id=gestor_id, titular_id=titular_id))

def centros_actualizar_vista():
    
    try:
        # Obtener el ID del gestor actual
        gestor_id = session.get('usuario_id')
        if not gestor_id:
            flash('No hay gestor autenticado', 'danger')
            return redirect(url_for('login'))

        # Obtener el ID del centro a actualizar
        centro_id = request.args.get('centro_id')
        if not centro_id:
            flash('ID de centro no proporcionado', 'danger')
            return redirect(url_for('centros.gestores_centros'))

        # Obtener el centro
        centro = db.centros.find_one({'_id': ObjectId(centro_id)})
        if not centro:
            flash('Centro no encontrado', 'danger')
            return redirect(url_for('centros.gestores_centros'))

        # Verificar que el titular del centro pertenece al gestor actual
        titular = db.usuarios_titulares.find_one({
            'usuario_id': centro['titular_id'],
            'gestor_id': ObjectId(gestor_id)
        })
        if not titular:
            flash('Centro no encontrado o no pertenece a este gestor', 'danger')
            return redirect(url_for('centros.gestores_centros'))

        # Obtener la información del titular
        titular_info = db.usuarios.find_one({'_id': centro['titular_id']})
        if not titular_info:
            flash('Titular no encontrado', 'danger')
            return redirect(url_for('centros.gestores_centros'))

        if request.method == 'GET':
            # Convertir ObjectId a string para el template
            centro['_id'] = str(centro['_id'])
            centro['titular_id'] = str(centro['titular_id'])
            centro['titular_info'] = {
                'alias': titular['alias'],
                'nombre': titular_info['nombre_usuario']
            }
            return render_template('gestores/centros/actualizar.html',
                                 centro=centro)

        if request.method == 'POST':
            # Obtener datos del formulario
            nombre_centro = request.form.get('nombre_centro', '').strip().upper()
            domicilio = request.form.get('domicilio', '').strip().upper()
            codigo_postal = request.form.get('codigo_postal', '').strip().upper()
            poblacion = request.form.get('poblacion', '').strip().upper()
            provincia = request.form.get('provincia', '').strip().upper()
            estado = request.form.get('estado', 'activo')

            # Validar datos
            if not all([nombre_centro, domicilio, codigo_postal, poblacion, provincia]):
                flash('Todos los campos son obligatorios', 'danger')
                return redirect(url_for('centros.gestores_centros_actualizar',
                                        centro_id=centro_id))

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
                        'estado': estado,
                        'fecha_actualizacion': datetime.now()
                    }
                }
            )
            if resultado.modified_count > 0:
                flash('Centro actualizado correctamente', 'success')
                return redirect(url_for('centros.gestores_centros'))
            else:
                flash('Error al actualizar el centro', 'danger')
                return redirect(url_for('centros.gestores_centros'))

    except Exception as e:
        flash(f'Error al actualizar el centro: {str(e)}', 'danger')
        return redirect(url_for('centros.gestores_centros'))

def centros_eliminar_vista():
    
    try:
        # Obtener el ID del gestor actual
        gestor_id = session.get('usuario_id')
        if not gestor_id:
            flash('No hay gestor autenticado', 'danger')
            return redirect(url_for('login'))

        # Obtener el ID del centro a eliminar
        centro_id = request.args.get('centro_id')
        if not centro_id:
            flash('ID de centro no proporcionado', 'danger')
            return redirect(url_for('centros.gestores_centros'))

        # Obtener el centro
        centro = db.centros.find_one({'_id': ObjectId(centro_id)})
        if not centro:
            flash('Centro no encontrado', 'danger')
            return redirect(url_for('centros.gestores_centros'))

        # Verificar que el titular del centro pertenece al gestor actual
        titular = db.usuarios_titulares.find_one({
            'usuario_id': centro['titular_id'],
            'gestor_id': ObjectId(gestor_id)
        })
        if not titular:
            flash('Centro no encontrado o no pertenece a este gestor', 'danger')
            return redirect(url_for('centros.gestores_centros'))

        # Eliminar el centro
        resultado = db.centros.delete_one({'_id': ObjectId(centro_id)})
        if resultado.deleted_count > 0:
            flash('Centro eliminado correctamente', 'success')
            return redirect(url_for('centros.gestores_centros'))
        else:
            flash('Error al eliminar el centro', 'danger')
            return redirect(url_for('centros.gestores_centros'))

    except Exception as e:
        flash(f'Error al eliminar el centro: {str(e)}', 'danger')
        return redirect(url_for('centros.gestores_centros'))