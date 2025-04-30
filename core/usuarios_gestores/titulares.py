from flask import render_template, session, flash, redirect, url_for, request
from bson.objectid import ObjectId
from datetime import datetime
from models.titulares_model import TitularesCollection
from utils.usuario_utils import obtener_usuario_autenticado
from utils.rol_utils import obtener_rol, verificar_rol_gestor
from utils.usuario_rol_utils import obtener_usuario_rol
from utils.gestor_utils import obtener_gestor_por_usuario
from config import conexion_mongo

db = conexion_mongo()

def verificaciones_consultas(gestor_id, titular_id=None):
    '''
    Función auxiliar para verificar permisos de gestor y obtener información necesaria
    Args:
        gestor_id (str): ID del gestor
        titular_id (str, optional): ID del titular a verificar
    
    Returns:
        - (False, respuesta_redireccion) si hay algún error
        - (True, (usuario, usuario_rol_gestor_id, gestor)) si todo está correcto
    '''
    # Obtener usuario autenticado y verificar permisos
    usuario, respuesta_redireccion = obtener_usuario_autenticado()
    if respuesta_redireccion:
        return False, respuesta_redireccion

    # Verificar rol de gestor
    tiene_rol, usuario_rol_gestor_id = verificar_rol_gestor(usuario['_id'])
    if not tiene_rol:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return False, redirect(url_for('usuarios.usuarios'))

    # Obtener el gestor asociado al usuario_rol_gestor_id
    gestor = obtener_gestor_por_usuario(gestor_id, usuario_rol_gestor_id)
    if not gestor:
        flash('Gestor no encontrado o no tienes permisos para acceder', 'danger')
        return False, redirect(url_for('usuarios_gestores.usuarios_gestores_gestor', 
                                       gestor_id=gestor_id
                                       ))

    # Si se proporciona un titular_id, verificar que pertenece al gestor
    if titular_id:
        titular = db.titulares.find_one({
            '_id': ObjectId(titular_id),
            'gestor_id': ObjectId(gestor_id)
        })
        if not titular:
            flash('Titular no encontrado o no pertenece a este gestor', 'danger')
            return False, redirect(url_for('ug_titulares.titulares', 
                                           gestor_id=gestor_id
                                           ))

    return True, (usuario, usuario_rol_gestor_id, gestor)

def titulares_vista(gestor_id):
    '''
    Vista para listar los titulares del gestor seleccionado
    '''
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id)
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_gestor_id, gestor = resultado
        nombre_gestor = gestor.get('nombre_gestor', 'Gestor')

        # Obtener parámetros de filtrado
        filtrar_titular = request.form.get('filtrar_titular', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('ug_titulares.titulares', 
                                    gestor_id=gestor_id
                                    ))

        # Construir la consulta base - buscar titulares donde el gestor_id sea el del gestor actual
        consulta_filtros = {'gestor_id': ObjectId(gestor_id)}
        
        # Aplicar filtros si existen
        if filtrar_estado != 'todos':
            consulta_filtros['estado_titular'] = filtrar_estado

        # Obtener los titulares asociados al gestor
        titulares = []
        titulares_gestor = db.titulares.find(consulta_filtros)
        
        for titular in titulares_gestor:
            # Si hay filtro por nombre, verificar si coincide
            if filtrar_titular:
                if (filtrar_titular.lower() not in titular['nombre_titular'].lower() and
                    filtrar_titular.lower() not in titular['cif_dni'].lower() and
                    filtrar_titular.lower() not in titular['telefono_titular'].lower()):
                    continue

            titulares.append({
                '_id': titular['_id'],
                'nombre_titular': titular['nombre_titular'],
                'cif_dni': titular['cif_dni'],
                'domicilio': titular['domicilio'],
                'codigo_postal': titular['codigo_postal'],
                'poblacion': titular['poblacion'],
                'provincia': titular['provincia'],
                'telefono_titular': titular['telefono_titular'],
                'estado_titular': titular['estado_titular']
            })

        return render_template('usuarios_gestores/titulares/listar.html', 
                                gestor_id=gestor_id,
                                nombre_gestor=nombre_gestor,
                                titulares=titulares,
                                filtrar_titular=filtrar_titular,
                                filtrar_estado=filtrar_estado
                                )

    except Exception as e:
        flash(f'Error al listar los titulares: {str(e)}', 'danger')
        return redirect(url_for('usuarios_gestores.usuarios_gestores_gestor', 
                                gestor_id=gestor_id
                                ))

def crear_titular(gestor_id, form_data):
    """
    Crea un nuevo titular en la base de datos.
    
    Args:
        gestor_id (str): ID del gestor
        datos_formulario (dict): Datos del formulario
    
    Returns:
        tuple: (bool, dict) 
            - bool: True si se creó exitosamente, False si hubo error
            - dict: Datos del formulario o mensaje de error
    """
    try:
        # Obtener los datos del formulario
        nombre_titular = form_data.get('nombre_titular').upper()
        cif_dni = form_data.get('cif_dni').upper()
        domicilio = form_data.get('domicilio')
        codigo_postal = form_data.get('codigo_postal')
        poblacion = form_data.get('poblacion').upper()
        provincia = form_data.get('provincia').upper()
        telefono_titular = form_data.get('telefono_titular')

        # Crear el titular
        titular = TitularesCollection(
            gestor_id=ObjectId(gestor_id),
            nombre_titular=nombre_titular,
            cif_dni=cif_dni,
            domicilio=domicilio,
            codigo_postal=codigo_postal,
            poblacion=poblacion,
            provincia=provincia,
            telefono_titular=telefono_titular,
            fecha_activacion=datetime.now(),
            fecha_modificacion=datetime.now(),
            fecha_inactivacion=None,
            estado_titular='activo'
        )

        # Insertar en la base de datos
        insert = db.titulares.insert_one(titular.__dict__)
        if insert.inserted_id:
            flash('Titular creado exitosamente', 'success')
            return True, None
        else:
            flash('Error al crear el titular', 'danger')
            return False, form_data

    except Exception as e:
        flash(f'Error al procesar el formulario: {str(e)}', 'danger')
        return False, form_data

def titulares_crear_vista(gestor_id):
    '''
    Vista para crear un titular del gestor seleccionado
    '''
    try:
        permisos_ok, resultado = verificaciones_consultas(gestor_id)
        if not permisos_ok:
            return resultado

        # Si es una petición POST, procesar el formulario
        if request.method == 'POST':
            creado, datos_formulario = crear_titular(gestor_id, request.form)
            if creado:
                return redirect(url_for('ug_titulares.titulares', 
                                        gestor_id=gestor_id
                                        ))
            else:
                return render_template('usuarios_gestores/titulares/crear.html',
                                       gestor_id=gestor_id,
                                       datos_formulario=datos_formulario
                                       )

        # Si es una petición GET, mostrar el formulario vacío
        return render_template('usuarios_gestores/titulares/crear.html',
                               gestor_id=gestor_id
                               )

    except Exception as e:
        flash(f'Error al acceder a la página: {str(e)}', 'danger')
        return redirect(url_for('ug_titulares.titulares', 
                                gestor_id=gestor_id
                                ))

def actualizar_titular(titular_id, form_data):
    """
    Actualiza un titular existente en la base de datos.
    
    Args:
        gestor_id (str): ID del gestor
        titular_id (str): ID del titular a actualizar
        form_data (dict): Datos del formulario
    
    Returns:
        tuple: (bool, dict) 
            - bool: True si se actualizó exitosamente, False si hubo error
            - dict: Datos del formulario o mensaje de error
    """
    try:
        # Obtener los datos del formulario
        nombre_titular = form_data.get('nombre_titular').upper()
        cif_dni = form_data.get('cif_dni').upper()
        domicilio = form_data.get('domicilio')
        codigo_postal = form_data.get('codigo_postal')
        poblacion = form_data.get('poblacion').upper()
        provincia = form_data.get('provincia').upper()
        telefono_titular = form_data.get('telefono_titular')
        estado_titular = form_data.get('estado_titular')

        # Actualizar el titular
        result = db.titulares.update_one(
            {'_id': ObjectId(titular_id)},
            {'$set': {
                'nombre_titular': nombre_titular,
                'cif_dni': cif_dni,
                'domicilio': domicilio,
                'codigo_postal': codigo_postal,
                'poblacion': poblacion,
                'provincia': provincia,
                'telefono_titular': telefono_titular,
                'estado_titular': estado_titular,
                'fecha_modificacion': datetime.now()
            }}
        )

        if result.modified_count > 0:
            flash('Titular actualizado exitosamente', 'success')
            return True, None
        else:
            flash('No se realizaron cambios en el titular', 'info')
            return True, None

    except Exception as e:
        flash(f'Error al procesar el formulario: {str(e)}', 'danger')
        return False, form_data

def titulares_actualizar_vista(gestor_id, titular_id):
    '''
    Vista para actualizar un titular del gestor seleccionado
    '''
    try:
        # Verificar permisos y que el titular pertenece al gestor
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id)
        if not permisos_ok:
            return resultado

        # Obtener el titular
        titular = db.titulares.find_one({'_id': ObjectId(titular_id)})

        # Si es una petición POST, procesar el formulario
        if request.method == 'POST':
            actualizar = actualizar_titular(titular_id, request.form)
            if actualizar:
                return redirect(url_for('ug_titulares.titulares', 
                                        gestor_id=gestor_id
                                        ))
            else:
                return render_template('usuarios_gestores/titulares/actualizar.html',
                                       gestor_id=gestor_id,
                                       titular=titular
                                       )

        # Si es una petición GET, mostrar el formulario con los datos del titular
        return render_template('usuarios_gestores/titulares/actualizar.html',
                               gestor_id=gestor_id,
                               titular=titular
                               )

    except Exception as e:
        flash(f'Error al acceder a la página: {str(e)}', 'danger')
        return redirect(url_for('ug_titulares.titulares', 
                                gestor_id=gestor_id
                                ))

def titulares_eliminar_vista(gestor_id, titular_id):
    '''
    Vista para eliminar un titular del gestor seleccionado
    '''
    try:
        # Verificar permisos y que el titular pertenece al gestor
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id)
        if not permisos_ok:
            return resultado

        # Eliminar el titular
        delete = db.titulares.delete_one({'_id': ObjectId(titular_id)})
        if delete.deleted_count > 0:
            flash('Titular eliminado exitosamente', 'success')
        else:
            flash('No se pudo eliminar el titular', 'danger')

        return redirect(url_for('ug_titulares.titulares', 
                                gestor_id=gestor_id
                                ))

    except Exception as e:
        flash(f'Error al eliminar el titular: {str(e)}', 'danger')
        return redirect(url_for('ug_titulares.titulares', 
                                gestor_id=gestor_id
                                ))

def titulares_titular_vista(gestor_id, titular_id):
    '''
    Vista para listar los usuarios titulares del titular seleccionado
    '''
    try:
        permisos_ok, resultado = verificaciones_consultas(gestor_id)
        if not permisos_ok:
            return resultado

        # Verificar que el titular pertenece al gestor actual
        titular = db.titulares.find_one({
            '_id': ObjectId(titular_id),
            'gestor_id': ObjectId(gestor_id)
        })
        if not titular:
            flash('Titular no encontrado o no pertenece a este gestor', 'danger')
            return redirect(url_for('usuarios_gestores.usuarios_gestores_gestor', 
                                    gestor_id=gestor_id
                                    ))

        # Obtener los usuarios titulares asociados al titular
        usuarios_titulares = list(db.usuarios_titulares.find({'titular_id': ObjectId(titular_id)}))

        return render_template('usuarios_gestores/titulares/index.html',
                               gestor_id=gestor_id,
                               titular_id=titular_id,
                               titular=titular,
                               usuarios_titulares=usuarios_titulares
                               )

    except Exception as e:
        flash(f'Error al acceder a la página: {str(e)}', 'danger')
        return redirect(url_for('ug_titulares.titulares', 
                                gestor_id=gestor_id
                                ))
