from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from datetime import datetime
from utils.usuario_utils import obtener_usuario_autenticado
from utils.rol_utils import obtener_rol, verificar_rol_gestor
from utils.usuario_rol_utils import obtener_usuario_rol
from models.gestores_model import GestoresCollection
from config import conexion_mongo

db = conexion_mongo()

def gestores_crear_vista():
    '''
    Vista para crear un nuevo gestor que se asignara al usuario autenticado con rol de gestor.
    '''
    try:
        # Obtener usuario autenticado y verificar permisos
        usuario, respuesta_redireccion = obtener_usuario_autenticado()
        if respuesta_redireccion:
            return respuesta_redireccion

        # Verificar rol de gestor
        tiene_rol, usuario_rol_id = verificar_rol_gestor(usuario['_id'])
        if not tiene_rol:
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        if request.method == 'POST':
            # Obtener datos del formulario
            nombre_gestor = request.form.get('nombre_gestor').upper()
            cif_dni = request.form.get('cif_dni').upper()
            domicilio = request.form.get('domicilio')
            codigo_postal = request.form.get('codigo_postal')
            poblacion = request.form.get('poblacion').upper()
            provincia = request.form.get('provincia').upper()
            telefono_gestor = request.form.get('telefono_gestor')

            # Crear instancia del modelo
            fecha_actual = datetime.now()
            nuevo_gestor = GestoresCollection(
                usuario_rol_id=usuario_rol_id,
                nombre_gestor=nombre_gestor,
                cif_dni=cif_dni,
                domicilio=domicilio,
                codigo_postal=codigo_postal,
                poblacion=poblacion,
                provincia=provincia,
                telefono_gestor=telefono_gestor,
                fecha_activacion=fecha_actual,
                fecha_modificacion=fecha_actual,
                fecha_inactivacion=None,
                estado_gestor='activo'
            )

            # Convertir el modelo a diccionario para MongoDB
            gestor_dict = nuevo_gestor.__dict__

            # Insertar en la base de datos
            resultado = db.gestores.insert_one(gestor_dict)

            if resultado.inserted_id:
                flash('Gestor creado exitosamente', 'success')
                return redirect(url_for('usuarios_gestores.usuarios_gestores'))
            else:
                flash('Error al crear el gestor', 'danger')

        return render_template('usuarios_gestores/gestores/crear.html',
                             usuario_rol_id=usuario_rol_id)

    except Exception as e:
        flash(f'Error al crear el gestor: {str(e)}', 'danger')
        return redirect(url_for('usuarios_gestores.usuarios_gestores'))

def gestores_actualizar_vista(gestor_id):
    '''
    Vista para actualizar un gestor relacionado con el usuario autenticado con rol de gestor. una vez actualizado el gestor, 
    se redirigira a la vista de usuarios gestores.
    '''
    try:
        # Obtener usuario autenticado y verificar permisos
        usuario, respuesta_redireccion = obtener_usuario_autenticado()
        if respuesta_redireccion:
            return respuesta_redireccion

        # Verificar rol de gestor
        tiene_rol, usuario_rol_id = verificar_rol_gestor(usuario['_id'])
        if not tiene_rol:
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        # Buscar el gestor
        gestor = db.gestores.find_one({
            '_id': ObjectId(gestor_id),
            'usuario_rol_id': usuario_rol_id
        })

        if request.method == 'POST':
            # Obtener datos del formulario
            nombre_gestor = request.form.get('nombre_gestor').upper()
            cif_dni = request.form.get('cif_dni').upper()
            domicilio = request.form.get('domicilio')
            codigo_postal = request.form.get('codigo_postal')
            poblacion = request.form.get('poblacion').upper()
            provincia = request.form.get('provincia').upper()
            telefono_gestor = request.form.get('telefono_gestor')
            estado_gestor = request.form.get('estado_gestor', 'activo')

            # Actualizar el gestor
            fecha_actual = datetime.now()
            resultado = db.gestores.update_one(
                {'_id': ObjectId(gestor_id)},
                {
                    '$set': {
                        'nombre_gestor': nombre_gestor,
                        'cif_dni': cif_dni,
                        'domicilio': domicilio,
                        'codigo_postal': codigo_postal,
                        'poblacion': poblacion,
                        'provincia': provincia,
                        'telefono_gestor': telefono_gestor,
                        'estado_gestor': estado_gestor,
                        'fecha_modificacion': fecha_actual
                    }
                }
            )

            if resultado.modified_count > 0:
                flash('Gestor actualizado exitosamente', 'success')
                return redirect(url_for('usuarios_gestores.usuarios_gestores'))
            else:
                flash('Error al actualizar el gestor', 'danger')

        # Convertir ObjectId a string para el template
        gestor['_id'] = str(gestor['_id'])
        return render_template('usuarios_gestores/gestores/actualizar.html',
                               gestor=gestor)

    except Exception as e:
        flash(f'Error al actualizar el gestor: {str(e)}', 'danger')
        return redirect(url_for('usuarios_gestores.usuarios_gestores'))

def gestores_eliminar_vista(gestor_id):
    try:
        # Obtener el ID del usuario actual
        usuario_id = session.get('usuario_id')
        
        if not usuario_id:
            flash('No hay usuario autenticado', 'danger')
            return redirect(url_for('login'))

        # Obtener el rol de gestor
        existe_rol, rol_gestor_id = obtener_rol('gestor')
        
        if not existe_rol:
            flash('Rol de gestor no encontrado', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        # Verificar si el usuario tiene el rol de gestor
        tiene_rol, usuario_rol_id = obtener_usuario_rol(usuario_id, rol_gestor_id)
        
        if not tiene_rol:
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        # Buscar el gestor
        gestor = db.gestores.find_one({
            '_id': ObjectId(gestor_id),
            'usuario_rol_id': usuario_rol_id
        })

        if not gestor:
            flash('Gestor no encontrado o no tienes permisos para eliminarlo', 'danger')
            return redirect(url_for('usuarios_gestores.usuarios_gestores'))

        # Eliminar el gestor de la base de datos
        resultado = db.gestores.delete_one({'_id': ObjectId(gestor_id)})

        if resultado.deleted_count > 0:
            flash('Gestor eliminado exitosamente', 'success')
        else:
            flash('Error al eliminar el gestor', 'danger')

        return redirect(url_for('usuarios_gestores.usuarios_gestores'))

    except Exception as e:
        flash(f'Error al eliminar el gestor: {str(e)}', 'danger')
        return redirect(url_for('usuarios_gestores.usuarios_gestores'))

