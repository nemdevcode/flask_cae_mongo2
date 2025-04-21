from flask import render_template, request, redirect, url_for, flash
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

def contratas_vista(gestor_id, titular_id):
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas(gestor_id, titular_id)
        if not permisos_ok:
            return resultado

        usuario, usuario_rol_id, gestor, titular = resultado
        nombre_gestor = gestor.get('nombre_gestor', 'Gestor')
        
        # Obtener parámetros de filtrado
        filtrar_contrata = request.form.get('filtrar_contrata', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')
        
        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('ug_contratas.contratas', gestor_id=gestor_id, titular_id=titular_id))
        
        # Construir la consulta base - buscar contratas donde el titular_id sea el del titular actual
        consulta_filtros = {'titular_id': ObjectId(titular_id)}
        
        # Aplicar filtros si existen
        if filtrar_estado != 'todos':
            consulta_filtros['estado_contrata'] = filtrar_estado
        
        # Obtener las contratas asociadas al titular
        contratas = []
        contratas_titular = db.contratas.find(consulta_filtros)
        
        for contrata in contratas_titular:
            # Si hay filtro por texto, verificar si coincide en algún campo
            if filtrar_contrata:
                if (filtrar_contrata.lower() not in contrata['nombre_contrata'].lower() and
                    filtrar_contrata.lower() not in contrata['cif_dni'].lower() and
                    filtrar_contrata.lower() not in contrata['domicilio_contrata'].lower() and
                    filtrar_contrata.lower() not in contrata['codigo_postal_contrata'].lower() and
                    filtrar_contrata.lower() not in contrata['poblacion_contrata'].lower() and
                    filtrar_contrata.lower() not in contrata['provincia_contrata'].lower() and
                    filtrar_contrata.lower() not in contrata.get('telefono_contrata', '').lower()):
                    continue

            contratas.append({
                '_id': str(contrata['_id']),
                'nombre_contrata': contrata['nombre_contrata'],
                'cif_dni': contrata['cif_dni'],
                'domicilio_contrata': contrata['domicilio_contrata'],
                'codigo_postal_contrata': contrata['codigo_postal_contrata'],
                'poblacion_contrata': contrata['poblacion_contrata'],
                'provincia_contrata': contrata['provincia_contrata'],
                'telefono_contrata': contrata.get('telefono_contrata', ''),
                'estado_contrata': contrata.get('estado_contrata', contrata.get('estado', 'activo'))
            })

        return render_template('usuarios_gestores/contratas/listar.html',
                               contratas=contratas,
                               titular=titular,
                               nombre_gestor=nombre_gestor,
                               filtrar_contrata=filtrar_contrata,
                               filtrar_estado=filtrar_estado,
                               gestor_id=gestor_id
                               )
                             
    except Exception as e:
        flash(f'Error al cargar las contratas: {str(e)}', 'danger')
        return redirect(url_for('ug_titulares.titulares_titular', gestor_id=gestor_id, titular_id=titular_id))

def contratas_crear_vista(gestor_id, titular_id):
    return render_template('usuarios_gestores/contratas/crear.html')

def contratas_actualizar_vista(contratata_id, datos_formulario):
    return render_template('usuarios_gestores/contratas/actualizar.html')

def contratas_eliminar_vista(gestor_id, titular_id, contratata_id):
    return render_template('usuarios_gestores/contratas/eliminar.html')

def contratas_contrata_vista(contratata_id):
    return render_template('usuarios_gestores/contratas/contrata.html')

