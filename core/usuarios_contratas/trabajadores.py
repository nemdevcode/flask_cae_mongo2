from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from datetime import datetime
from config import conexion_mongo
from models.trabajadores_model import TrabajadoresCollection

db = conexion_mongo()

def trabajadores_vista(usuario_rol_contrata_id, contrata_id):
    '''
    Vista de usuarios de contratas para gestionar trabajadores.
    '''
    try:
        # Obtener nombre de la contrata
        nombre_contrata = db.contratas.find_one({'_id': ObjectId(contrata_id)})['nombre_contrata']

        # Obtener parámetros de filtrado
        filtrar_trabajador = request.form.get('filtrar_trabajador', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')
        
        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('ucon_trabajadores.trabajadores', 
                                    usuario_rol_contrata_id=usuario_rol_contrata_id, 
                                    contrata_id=contrata_id
                                    ))
        
        # Construir la consulta base - buscar trabajadores de la contratas
        consulta_filtros = {'contrata_id': ObjectId(contrata_id)}

        # Aplicar filtros si existen
        if filtrar_estado != 'todos':
            consulta_filtros['estado_trabajador'] = filtrar_estado
        
        # Obtener los trabajadores de la contrata
        trabajadores = []
        trabajadores_contrata = db.trabajadores.find(consulta_filtros)

        for trabajador in trabajadores_contrata:
            # Si hay filtro por texto, verificar si coincide en algún campo
            if filtrar_trabajador:
                if (filtrar_trabajador.lower() not in trabajador['nombre_trabajador'].lower() and
                    filtrar_trabajador.lower() not in trabajador['apellidos_trabajador'].lower() and
                    filtrar_trabajador.lower() not in trabajador['dni_nie'].lower() and
                    filtrar_trabajador.lower() not in trabajador['puesto_trabajo'].lower() and
                    filtrar_trabajador.lower() not in trabajador['categoria_profesional'].lower()):
                    continue
            
            trabajadores.append(
                {
                    '_id': str(trabajador['_id']),
                    'nombre_trabajador': trabajador['nombre_trabajador'],
                    'apellidos_trabajador': trabajador['apellidos_trabajador'],
                    'dni_nie': trabajador['dni_nie'],
                    'puesto_trabajo': trabajador['puesto_trabajo'],
                    'categoria_profesional': trabajador['categoria_profesional'],
                    'estado_trabajador': trabajador['estado_trabajador']
                }
            )
            
        return render_template('usuarios_contratas/trabajadores/listar.html',
                               usuario_rol_contrata_id=usuario_rol_contrata_id,
                               contrata_id=contrata_id,
                               nombre_contrata=nombre_contrata,
                               trabajadores=trabajadores,
                               filtrar_trabajador=filtrar_trabajador,
                               filtrar_estado=filtrar_estado)
    except Exception as e:
        flash(f'Error al cargar la vista de trabajadores: {str(e)}', 'danger')
        return redirect(url_for('usuarios_contratas.usuarios_contratas_contrata_vista',
                                usuario_rol_contrata_id=usuario_rol_contrata_id,
                                contrata_id=contrata_id))

def crear_trabajador(contrata_id, datos_formulario):
    '''
    Crea un trabajador.
    '''
    try:
        # Obtener los datos del formulario
        nombre_trabajador = datos_formulario.get('nombre_trabajador').upper()
        apellidos_trabajador = datos_formulario.get('apellidos_trabajador').upper()
        dni_nie = datos_formulario.get('dni_nie').upper()
        puesto_trabajo = datos_formulario.get('puesto_trabajo').upper()
        categoria_profesional = datos_formulario.get('categoria_profesional').upper()

        # Verificar que no existe un trabajador con el mismo dni_nie
        if db.trabajadores.find_one({'dni_nie': dni_nie}):
            flash('Ya existe un trabajador con este DNI/NIE', 'danger')
            return False, datos_formulario

        # Crear instancia de TrabajadoresCollection
        trabajador = TrabajadoresCollection(
            contrata_id=ObjectId(contrata_id),
            nombre_trabajador=nombre_trabajador,
            apellidos_trabajador=apellidos_trabajador,
            dni_nie=dni_nie,
            puesto_trabajo=puesto_trabajo,
            categoria_profesional=categoria_profesional,
            fecha_activacion=datetime.now(),
            fecha_modificacion=datetime.now(),
            fecha_inactivacion=None,
            estado_trabajador='activo'
        )

        # Insertar el trabajador en la base de datos
        insert = db.trabajadores.insert_one(trabajador.to_dict())
    
        if insert.inserted_id:
                flash('Trabajador creado correctamente', 'success')
                return True, None
        else:
            flash('Error al crear el trabajador', 'danger')
            return False, datos_formulario
            
    except Exception as e:
        flash(f'Error al procesar el formulario: {str(e)}', 'danger')
        return False, datos_formulario

def trabajadores_crear_vista(usuario_rol_contrata_id, contrata_id):
    '''
    Vista de usuarios de contratas para crear trabajadores.
    '''
    try:
        # Si es una petición POST, procesar el formulario
        if request.method == 'POST':
            creado, datos_formulario = crear_trabajador(contrata_id, request.form)
            if creado:
                return redirect(url_for('ucon_trabajadores.trabajadores',
                                        usuario_rol_contrata_id=usuario_rol_contrata_id,
                                        contrata_id=contrata_id))
            else:
                return render_template('usuarios_contratas/trabajadores/crear.html',
                                usuario_rol_contrata_id=usuario_rol_contrata_id,
                                contrata_id=contrata_id,
                                datos_formulario=datos_formulario)
            
        # Si es una petición GET, mostrar el formulario vacío
        return render_template('usuarios_contratas/trabajadores/crear.html',
                                usuario_rol_contrata_id=usuario_rol_contrata_id,
                                contrata_id=contrata_id)

    except Exception as e:
        flash(f'Error al crear el trabajador: {str(e)}', 'danger')
        return redirect(url_for('ucon_trabajadores.trabajadores_crear',
                                usuario_rol_contrata_id=usuario_rol_contrata_id,
                                contrata_id=contrata_id))

def actualizar_trabajador(trabajador_id, datos_formulario):
    '''
    Actualiza un trabajador.
    '''
    try:
        # Obtener los datos del formulario
        nombre_trabajador = datos_formulario.get('nombre_trabajador').upper()
        apellidos_trabajador = datos_formulario.get('apellidos_trabajador').upper()
        dni_nie = datos_formulario.get('dni_nie').upper()
        puesto_trabajo = datos_formulario.get('puesto_trabajo').upper()
        categoria_profesional = datos_formulario.get('categoria_profesional').upper()
        estado_trabajador = datos_formulario.get('estado_trabajador')

        # Obtener el trabajador actual
        trabajador_actual = db.trabajadores.find_one({'_id': ObjectId(trabajador_id)})
        
        # Verificar DNI/NIE solo si ha cambiado
        if dni_nie != trabajador_actual['dni_nie']:
            if db.trabajadores.find_one({'dni_nie': dni_nie}):
                flash('Ya existe un trabajador con este DNI/NIE', 'danger')
                return False, datos_formulario

        # Actualizar el trabajador en la base de datos
        update = db.trabajadores.update_one({
            '_id': ObjectId(trabajador_id)
        }, {
            '$set': {
                'nombre_trabajador': nombre_trabajador,
                'apellidos_trabajador': apellidos_trabajador,
                'dni_nie': dni_nie,
                'puesto_trabajo': puesto_trabajo,
                'categoria_profesional': categoria_profesional,
                'fecha_modificacion': datetime.now(),
                'fecha_inactivacion': None,
                'estado_trabajador': estado_trabajador
            }
        })

        if update.modified_count > 0:
            flash('Trabajador actualizado exitosamente', 'success')
            return True, None
        else:
            flash('Error al actualizar el trabajador', 'danger')
            return False, datos_formulario
        
    except Exception as e:
        flash(f'Error al actualizar el trabajador: {str(e)}', 'danger')
        return False, datos_formulario

def trabajadores_actualizar_vista(usuario_rol_contrata_id, contrata_id, trabajador_id):
    '''
    Vista de usuarios de contratas para actualizar trabajadores.
    '''
    try:
        # Obtener el trabajador a actualizar
        trabajador = db.trabajadores.find_one({
            '_id': ObjectId(trabajador_id)
        })

        # Si es una petición POST, procesar el formulario
        if request.method == 'POST':
            actualizado, datos_formulario = actualizar_trabajador(trabajador_id, request.form)
            if actualizado:
                return redirect(url_for('ucon_trabajadores.trabajadores',
                                        usuario_rol_contrata_id=usuario_rol_contrata_id,
                                        contrata_id=contrata_id
                                        ))
            else:
                return render_template('usuarios_contratas/trabajadores/actualizar.html',
                                        usuario_rol_contrata_id=usuario_rol_contrata_id,
                                        contrata_id=contrata_id,
                                        trabajador=trabajador,
                                        datos_formulario=datos_formulario
                                        )

        return render_template('usuarios_contratas/trabajadores/actualizar.html', 
                           usuario_rol_contrata_id=usuario_rol_contrata_id, 
                           contrata_id=contrata_id, 
                           trabajador=trabajador
                           )

    except Exception as e:
        flash(f'Error al actualizar el trabajador: {str(e)}', 'danger')
        return redirect(url_for('ucon_trabajadores.trabajadores_actualizar',
                                usuario_rol_contrata_id=usuario_rol_contrata_id,
                                contrata_id=contrata_id,
                                trabajador_id=trabajador_id
                                ))

def asignar_trabajador_centro(trabajador_id, estados_centros):
    '''
    Asigna o actualiza centros a un trabajador.
    '''
    try:
        # Obtener las asignaciones actuales del trabajador
        asignaciones_actuales = db.trabajadores_centros.find(
            {'trabajador_id': ObjectId(trabajador_id)}
        )
        
        # Convertir a diccionario para fácil acceso
        asignaciones_actuales_dict = {
            str(asig['centro_id']): asig 
            for asig in asignaciones_actuales
        }

        # Procesar cada centro
        for centro_id, estado in estados_centros.items():
            centro_id = ObjectId(centro_id)

            if estado == 'no_asignado':
                # Si el estado es no_asignado, desactivar la asignación
                if str(centro_id) in asignaciones_actuales_dict:
                    db.trabajadores_centros.update_one(
                        {
                            'trabajador_id': ObjectId(trabajador_id),
                            'centro_id': centro_id
                        },
                        {
                            '$set': {
                                'estado_trabajador_centro': 'inactivo',
                                'fecha_modificacion': datetime.now()
                            }
                        }
                    )
            else:
                # Para estados activo o inactivo
                if str(centro_id) in asignaciones_actuales_dict:
                    # Actualizar asignación existente
                    db.trabajadores_centros.update_one(
                        {
                            'trabajador_id': ObjectId(trabajador_id),
                            'centro_id': centro_id
                        },
                        {
                            '$set': {
                                'estado_trabajador_centro': estado,
                                'fecha_modificacion': datetime.now()
                            }
                        }
                    )
                else:
                    # Crear nueva asignación
                    db.trabajadores_centros.insert_one({
                        'trabajador_id': ObjectId(trabajador_id),
                        'centro_id': centro_id,
                        'estado_trabajador_centro': estado,
                        'fecha_activacion': datetime.now(),
                        'fecha_modificacion': datetime.now()
                    })

        return True

    except Exception as e:
        flash(f'Error al asignar centros al trabajador: {str(e)}', 'danger')
        return False

def trabajadores_asignacion_centros_vista(usuario_rol_contrata_id, contrata_id, trabajador_id):
    '''
    Asigna centros a un trabajador.
    '''
    try:
        if request.method == 'POST':
            # Obtener estados de todos los centros
            estados_centros = {}
            for key, value in request.form.items():
                if key.startswith('estado_trabajador_centro_'):
                    centro_id = key.split('_')[-1]
                    estados_centros[centro_id] = value

            # Asignar centros al trabajador
            if asignar_trabajador_centro(trabajador_id, estados_centros):
                flash('Centros asignados correctamente', 'success')
            else:
                flash('Error al asignar centros', 'danger')

            return redirect(url_for('ucon_trabajadores.trabajadores',
                                    usuario_rol_contrata_id=usuario_rol_contrata_id,
                                    contrata_id=contrata_id))

        # Obtener nombre del trabajador
        trabajador = db.trabajadores.find_one({'_id': ObjectId(trabajador_id)})
        nombre_completo_trabajador = f"{trabajador['nombre_trabajador']} {trabajador['apellidos_trabajador']}"

        # Obtener id del titular de la contrata
        titular_id = db.contratas.find_one({'_id': ObjectId(contrata_id)})['titular_id']

        # Obtener los centros de la contrata
        nombres_centros = db.centros.find({'titular_id': ObjectId(titular_id)}, {'_id': 1, 'nombre_centro': 1})

        # Obtener los centros asignados al trabajador
        centros_asignados = db.trabajadores_centros.find(
            {'trabajador_id': ObjectId(trabajador_id)}, 
            {'_id': 1, 'centro_id': 1, 'estado_trabajador_centro': 1}
        )
        
        # Convertir a lista de IDs y estados para facilitar la verificación en el template
        centros_asignados_info = {
            str(centro['centro_id']): centro['estado_trabajador_centro'] 
            for centro in centros_asignados
        }

        # Obtener los centros no asignados al trabajador
        centros_no_asignados = []
        for centro in nombres_centros:
            centro_id = str(centro['_id'])
            if centro_id not in centros_asignados_info:
                centro['estado_trabajador_centro'] = None  # Sin estado por defecto
                centros_no_asignados.append(centro)
            else:
                centro['estado_trabajador_centro'] = centros_asignados_info[centro_id]
                centros_no_asignados.append(centro)

        return render_template('usuarios_contratas/trabajadores/index.html',
                                usuario_rol_contrata_id=usuario_rol_contrata_id,
                                contrata_id=contrata_id,
                                trabajador_id=trabajador_id,
                                nombre_completo_trabajador=nombre_completo_trabajador,
                                centros_asignados=centros_asignados_info,
                                centros_no_asignados=centros_no_asignados
                                )

    except Exception as e:
        flash(f'Error al asignar centros al trabajador: {str(e)}', 'danger')
        return redirect(url_for('ucon_trabajadores.trabajadores',
                                usuario_rol_contrata_id=usuario_rol_contrata_id,
                                contrata_id=contrata_id
                                ))


