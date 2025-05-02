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

def titulares_crear_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id):
    return render_template('usuarios_cogestores/titulares/crear.html',
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                           usuario_rol_gestor_id=usuario_rol_gestor_id,
                           gestor_id=gestor_id
                           )

def titulares_actualizar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, form_data):
    '''
    Vista para actualizar un titular
    '''
    # Obtener el titular a actualizar
    titular = db.titulares.find_one({
        '_id': ObjectId(titular_id),
        'gestor_id': ObjectId(gestor_id)
    })
    
    # Obtener los datos del formulario
    nombre_titular = form_data.get('nombre_titular')
    cif_dni = form_data.get('cif_dni')
    domicilio = form_data.get('domicilio')
    codigo_postal = form_data.get('codigo_postal')
    poblacion = form_data.get('poblacion')
    provincia = form_data.get('provincia')
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
            'estado_titular': estado_titular
        }}
    )

    if result.modified_count > 0:
        flash('Titular actualizado exitosamente', 'success')
    else:
        flash('No se realizaron cambios en el titular', 'info')

    # Redirigir a la vista de titulares
    return redirect(url_for('uc_titulares.titulares',
                            usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                            usuario_rol_gestor_id=usuario_rol_gestor_id,
                            gestor_id=gestor_id
                            ))

    return render_template('usuarios_cogestores/titulares/actualizar.html',
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                           usuario_rol_gestor_id=usuario_rol_gestor_id,
                           gestor_id=gestor_id,
                           titular_id=titular_id,
                           titular=titular
                           )

def titulares_eliminar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    return render_template('usuarios_cogestores/titulares/eliminar.html',
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                           usuario_rol_gestor_id=usuario_rol_gestor_id,
                           gestor_id=gestor_id,
                           titular_id=titular_id
                           )

def titulares_titular_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    return render_template('usuarios_cogestores/titulares/index.html',
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                           usuario_rol_gestor_id=usuario_rol_gestor_id,
                           gestor_id=gestor_id,
                           titular_id=titular_id
                           )

