from flask import render_template, session, flash, redirect, url_for, request
from bson.objectid import ObjectId
from config import conexion_mongo
from models.titulares_model import TitularesCollection
from utils.usuario_rol_utils import obtener_rol, obtener_usuario_rol
from datetime import datetime

db = conexion_mongo()

def gestores_titulares_vista(gestor_id):
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

        # Obtener el gestor asociado al usuario_rol_id
        gestor = db.gestores.find_one({
            '_id': ObjectId(gestor_id),
            'usuario_rol_id': usuario_rol_id,
            'estado_gestor': 'activo'
        })
        if not gestor:
            flash('Gestor no encontrado o no tienes permisos para acceder', 'danger')
            return redirect(url_for('gestores.gestores_titulares', gestor_id=gestor_id))

        # Obtener la información del usuario
        usuario = db.usuarios.find_one({'_id': ObjectId(usuario_id)})
        if not usuario:
            flash('Usuario no encontrado', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        nombre_gestor = gestor.get('nombre_gestor', 'Gestor')

        # Obtener parámetros de filtrado
        filtrar_titular = request.form.get('filtrar_titular', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('gestores.gestores_titulares', gestor_id=gestor_id))

        # Construir la consulta base - buscar titulares donde el gestor_id sea el del gestor actual
        query = {'gestor_id': ObjectId(gestor_id)}
        
        # Aplicar filtros si existen
        if filtrar_estado != 'todos':
            query['estado_titular'] = filtrar_estado

        # Obtener los titulares asociados al gestor
        titulares = []
        titulares_cursor = db.titulares.find(query)
        
        for titular in titulares_cursor:
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
                             titulares=titulares,
                             nombre_gestor=nombre_gestor,
                             filtrar_titular=filtrar_titular,
                             filtrar_estado=filtrar_estado,
                             gestor_id=gestor_id)

    except Exception as e:
        flash(f'Error al listar los titulares: {str(e)}', 'danger')
        return redirect(url_for('gestores.usuarios_gestores_gestor', gestor_id=gestor_id))

def gestores_titulares_crear_vista(gestor_id):
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

        # Obtener el gestor asociado al usuario_rol_id y gestor_id
        gestor = db.gestores.find_one({
            '_id': ObjectId(gestor_id),
            'usuario_rol_id': usuario_rol_id,
            'estado_gestor': 'activo'
        })
        if not gestor:
            flash('Gestor no encontrado o no tienes permisos para acceder', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        # Si es una petición POST, procesar el formulario
        if request.method == 'POST':
            try:
                # Obtener los datos del formulario
                nombre_titular = request.form.get('nombre_titular').upper()
                cif_dni = request.form.get('cif_dni').upper()
                domicilio = request.form.get('domicilio')
                codigo_postal = request.form.get('codigo_postal')
                poblacion = request.form.get('poblacion').upper()
                provincia = request.form.get('provincia').upper()
                telefono_titular = request.form.get('telefono_titular')

                # Validar campos requeridos
                if not all([nombre_titular, cif_dni, domicilio, codigo_postal, poblacion, provincia, telefono_titular]):
                    flash('Todos los campos son obligatorios', 'danger')
                    return render_template('usuarios_gestores/titulares/crear.html', 
                                         form_data=request.form,
                                         gestor_id=gestor_id)

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
                result = db.titulares.insert_one(titular.__dict__)
                if result.inserted_id:
                    flash('Titular creado exitosamente', 'success')
                    return redirect(url_for('gestores.gestores_titulares', gestor_id=gestor_id))
                else:
                    flash('Error al crear el titular', 'danger')
                    return render_template('usuarios_gestores/titulares/crear.html', 
                                         form_data=request.form,
                                         gestor_id=gestor_id)

            except Exception as e:
                flash(f'Error al procesar el formulario: {str(e)}', 'danger')
                return render_template('usuarios_gestores/titulares/crear.html', 
                                     form_data=request.form,
                                     gestor_id=gestor_id)

        # Si es una petición GET, mostrar el formulario vacío
        return render_template('usuarios_gestores/titulares/crear.html',
                             gestor_id=gestor_id)

    except Exception as e:
        flash(f'Error al acceder a la página: {str(e)}', 'danger')
        return redirect(url_for('gestores.gestores_titulares', gestor_id=gestor_id))

def gestores_titulares_actualizar_vista(titular_id, gestor_id):
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

        # Obtener el gestor asociado al usuario_rol_id y gestor_id
        gestor = db.gestores.find_one({
            '_id': ObjectId(gestor_id),
            'usuario_rol_id': usuario_rol_id,
            'estado_gestor': 'activo'
        })
        if not gestor:
            flash('Gestor no encontrado o no tienes permisos para acceder', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        # Obtener el titular
        titular = db.titulares.find_one({'_id': ObjectId(titular_id), 'gestor_id': ObjectId(gestor_id)})
        if not titular:
            flash('Titular no encontrado', 'danger')
            return redirect(url_for('gestores.gestores_titulares', gestor_id=gestor_id))

        # Si es una petición POST, procesar el formulario
        if request.method == 'POST':
            try:
                # Obtener los datos del formulario
                nombre_titular = request.form.get('nombre_titular').upper()
                cif_dni = request.form.get('cif_dni').upper()
                domicilio = request.form.get('domicilio')
                codigo_postal = request.form.get('codigo_postal')
                poblacion = request.form.get('poblacion').upper()
                provincia = request.form.get('provincia').upper()
                telefono_titular = request.form.get('telefono_titular')
                estado_titular = request.form.get('estado_titular')

                # Validar campos requeridos
                if not all([nombre_titular, cif_dni, domicilio, codigo_postal, poblacion, provincia, telefono_titular, estado_titular]):
                    flash('Todos los campos son obligatorios', 'danger')
                    return render_template('usuarios_gestores/titulares/actualizar.html', 
                                         titular=titular,
                                         gestor_id=gestor_id)

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
                    return redirect(url_for('gestores.gestores_titulares', gestor_id=gestor_id))
                else:
                    flash('No se realizaron cambios en el titular', 'info')
                    return redirect(url_for('gestores.gestores_titulares', gestor_id=gestor_id))

            except Exception as e:
                flash(f'Error al procesar el formulario: {str(e)}', 'danger')
                return render_template('usuarios_gestores/titulares/actualizar.html', 
                                     titular=titular,
                                     gestor_id=gestor_id)

        # Si es una petición GET, mostrar el formulario con los datos del titular
        return render_template('usuarios_gestores/titulares/actualizar.html', 
                             titular=titular,
                             gestor_id=gestor_id)

    except Exception as e:
        flash(f'Error al acceder a la página: {str(e)}', 'danger')
        return redirect(url_for('gestores.gestores_titulares', gestor_id=gestor_id))

def gestores_titulares_eliminar_vista(titular_id, gestor_id):
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

        # Obtener el gestor asociado al usuario_rol_id
        gestor = db.gestores.find_one({'usuario_rol_id': ObjectId(usuario_rol_id)})
        if not gestor:
            flash('Gestor no encontrado', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        # Verificar que el titular pertenece al gestor actual
        titular = db.titulares.find_one({
            '_id': ObjectId(titular_id),
            'gestor_id': ObjectId(gestor_id)
        })

        if not titular:
            flash('Titular no encontrado o no pertenece a este gestor', 'danger')
            return redirect(url_for('gestores.gestores_titulares', gestor_id=gestor_id))

        # Eliminar el titular
        result = db.titulares.delete_one({'_id': ObjectId(titular_id)})
        if result.deleted_count > 0:
            flash('Titular eliminado exitosamente', 'success')
        else:
            flash('No se pudo eliminar el titular', 'danger')

        return redirect(url_for('gestores.gestores_titulares', gestor_id=gestor_id))

    except Exception as e:
        flash(f'Error al eliminar el titular: {str(e)}', 'danger')
        return redirect(url_for('gestores.gestores_titulares', gestor_id=gestor_id))

def gestores_titulares_titular_vista(gestor_id, titular_id):
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

        # Obtener el gestor asociado al usuario_rol_id y gestor_id
        gestor = db.gestores.find_one({
            '_id': ObjectId(gestor_id),
            'usuario_rol_id': usuario_rol_id,
            'estado_gestor': 'activo'
        })
        if not gestor:
            flash('Gestor no encontrado o no tienes permisos para acceder', 'danger')
            return redirect(url_for('gestores.usuarios_gestores_gestor', gestor_id=gestor_id))

        # Verificar que el titular pertenece al gestor actual
        titular = db.titulares.find_one({
            '_id': ObjectId(titular_id),
            'gestor_id': ObjectId(gestor_id)
        })
        if not titular:
            flash('Titular no encontrado o no pertenece a este gestor', 'danger')
            return redirect(url_for('gestores.usuarios_gestores_gestor', gestor_id=gestor_id))

        # Obtener los usuarios titulares asociados al titular
        usuarios_titulares = list(db.usuarios_titulares.find({'titular_id': ObjectId(titular_id)}))

        return render_template('usuarios_gestores/usuarios_titulares/listar.html', 
                             titular=titular,
                             titular_id=titular_id,
                             gestor_id=gestor_id,
                             usuarios_titulares=usuarios_titulares)

    except Exception as e:
        flash(f'Error al acceder a la página: {str(e)}', 'danger')
        return redirect(url_for('gestores.usuarios_gestores_gestor', gestor_id=gestor_id))
