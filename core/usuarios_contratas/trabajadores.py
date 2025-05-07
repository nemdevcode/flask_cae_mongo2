from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from datetime import datetime
from utils.usuario_utils import obtener_usuario_autenticado
from utils.rol_utils import verificar_rol_contrata
from config import conexion_mongo

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

        # Insertar la contrata en la base de datos
        insert = db.trabajadores.insert_one({
            'contrata_id': ObjectId(contrata_id),
            'nombre_trabajador': nombre_trabajador,
            'apellidos_trabajador': apellidos_trabajador,
            'dni_nie': dni_nie,
            'puesto_trabajo': puesto_trabajo,
            'categoria_profesional': categoria_profesional,
            'fecha_activacion': datetime.now(),
            'fecha_modificacion': datetime.now(),
            'fecha_inactivacion': None,
            'estado_trabajador': 'activo'
        })
    
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




