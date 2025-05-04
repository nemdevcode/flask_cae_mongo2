from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from datetime import datetime
from utils.usuario_utils import obtener_usuario_autenticado
from utils.rol_utils import obtener_rol, verificar_rol_cogestor
from utils.usuario_rol_utils import obtener_usuario_rol
from models.gestores_model import GestoresCollection
from config import conexion_mongo

db = conexion_mongo()

def titulares_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id):
    '''
    Vista para listar los titulares de un gestor_id seleccionado
    '''

    # Obtener parámetros de filtrado
    filtrar_titular = request.form.get('filtrar_titular', '')
    filtrar_estado = request.form.get('filtrar_estado', 'todos')
    vaciar = request.args.get('vaciar', '0')

    # Si se solicita vaciar filtros
    if vaciar == '1':
        return redirect(url_for('uc_titulares.titulares',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
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
    # Obtener el nombre del gestor seleccionado
    gestor = db.gestores.find_one({
            '_id': ObjectId(gestor_id),
            'usuario_rol_gestor_id': ObjectId(usuario_rol_gestor_id)
        }, {'nombre_gestor': 1, '_id': 0})

    return render_template('usuarios_cogestores/titulares/listar.html',
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                           usuario_rol_gestor_id=usuario_rol_gestor_id,
                           gestor_id=gestor_id,
                           gestor=gestor,
                           titulares=titulares,
                           filtrar_titular=filtrar_titular,
                           filtrar_estado=filtrar_estado
                           )

def crear_titular(gestor_id, datos_formulario):
    '''
    Crea un nuevo titular en la base de datos.
    '''
    try:
        # Obtener los datos del formulario
        nombre_titular = datos_formulario.get('nombre_titular')
        cif_dni = datos_formulario.get('cif_dni')
        domicilio = datos_formulario.get('domicilio')
        codigo_postal = datos_formulario.get('codigo_postal')
        poblacion = datos_formulario.get('poblacion')
        provincia = datos_formulario.get('provincia')
        telefono_titular = datos_formulario.get('telefono_titular')

        # Insertar el titular en la base de datos
        insert = db.titulares.insert_one({
            'gestor_id': ObjectId(gestor_id),
            'nombre_titular': nombre_titular,
            'cif_dni': cif_dni,
            'domicilio': domicilio,
            'codigo_postal': codigo_postal,
            'poblacion': poblacion,
            'provincia': provincia,
            'telefono_titular': telefono_titular,
            'estado_titular': 'activo',
            'fecha_activacion': datetime.now(),
            'fecha_modificacion': datetime.now(),
            'fecha_inactivacion': None
        })

        if insert.inserted_id:
            flash('Titular creado exitosamente', 'success')
            return True, None
        else:
            flash('Error al crear el titular', 'danger')
            return False, datos_formulario
    except Exception as e:
        flash(f'Error al procesar el formulario: {str(e)}', 'danger')
        return False, datos_formulario

def titulares_crear_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id):
    '''
    Vista para crear un titular
    '''
    try:
        # Si es una petición POST, procesar el formulario
        if request.method == 'POST':
            creado, datos_formulario = crear_titular(gestor_id, request.form)
            if creado:
                return redirect(url_for('uc_titulares.titulares',
                                        usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                        usuario_rol_gestor_id=usuario_rol_gestor_id,
                                        gestor_id=gestor_id
                                        ))
            else:
                return render_template('usuarios_cogestores/titulares/crear.html',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id,
                                datos_formulario=datos_formulario
                                )

        # Si es una petición GET, mostrar el formulario vacío
        return render_template('usuarios_cogestores/titulares/crear.html',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id
                                )

    except Exception as e:
        flash(f'Error al crear el titular: {str(e)}', 'danger')
        return redirect(url_for('uc_titulares.titulares',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id
                                ))

def actualizar_titular(titular_id, gestor_id, datos_formulario):
    '''
    Actualiza un titular existente en la base de datos.
    '''
    try:       
        # Obtener los datos del formulario
        nombre_titular = datos_formulario.get('nombre_titular')
        cif_dni = datos_formulario.get('cif_dni')
        domicilio = datos_formulario.get('domicilio')
        codigo_postal = datos_formulario.get('codigo_postal')
        poblacion = datos_formulario.get('poblacion')
        provincia = datos_formulario.get('provincia')
        telefono_titular = datos_formulario.get('telefono_titular')
        estado_titular = datos_formulario.get('estado_titular')

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
                'estado_titular': estado_titular
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
        return False, datos_formulario


def titulares_actualizar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    '''
    Vista para actualizar un titular
    '''

    try:
        # Obtener el titular a actualizar
        titular = db.titulares.find_one({
            '_id': ObjectId(titular_id),
            'gestor_id': ObjectId(gestor_id)
        })
        
        # Si es una petición POST, procesar el formulario
        if request.method == 'POST':
            actualizar = actualizar_titular(titular_id, gestor_id, request.form)
            if actualizar:
                return redirect(url_for('uc_titulares.titulares', 
                                        usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                        usuario_rol_gestor_id=usuario_rol_gestor_id,
                                        gestor_id=gestor_id
                                        ))
            else:
                return render_template('usuarios_cogestores/titulares/actualizar.html',
                                       gestor_id=gestor_id,
                                       titular=titular
                                       )
  

        return render_template('usuarios_cogestores/titulares/actualizar.html',
                            usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                            usuario_rol_gestor_id=usuario_rol_gestor_id,
                            gestor_id=gestor_id,
                            titular_id=titular_id,
                            titular=titular
                            )

    except Exception as e:
        flash(f'Error al actualizar el titular: {str(e)}', 'danger')
        return redirect(url_for('uc_titulares.titulares',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id
                                ))
    
def titulares_eliminar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    try:
        # Eliminar el titular
        delete = db.titulares.delete_one({
            '_id': ObjectId(titular_id),
            'gestor_id': ObjectId(gestor_id)
        })
        if delete.deleted_count > 0:
            flash('Titular eliminado exitosamente', 'success')
        else:
            flash('No se pudo eliminar el titular', 'danger')

        return redirect(url_for('uc_titulares.titulares',
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                           usuario_rol_gestor_id=usuario_rol_gestor_id,
                           gestor_id=gestor_id,
                           titular_id=titular_id
                           ))
    except Exception as e:
        flash(f'Error al eliminar el titular: {str(e)}', 'danger')
        return redirect(url_for('uc_titulares.titulares',
                                usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                                usuario_rol_gestor_id=usuario_rol_gestor_id,
                                gestor_id=gestor_id
                                ))

def titulares_titular_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    return render_template('usuarios_cogestores/titulares/index.html',
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                           usuario_rol_gestor_id=usuario_rol_gestor_id,
                           gestor_id=gestor_id,
                           titular_id=titular_id
                           )

