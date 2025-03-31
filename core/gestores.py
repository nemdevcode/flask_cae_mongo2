from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from config import conexion_mongo
from utils.usuario_rol_utils import obtener_rol, obtener_usuario_rol
from models.gestores_model import GestoresCollection
from datetime import datetime

db = conexion_mongo()

def gestores_crear_vista():
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

        if request.method == 'POST':
            # Obtener datos del formulario
            nombre_gestor = request.form.get('nombre_gestor')
            cif_dni = request.form.get('cif_dni')
            domicilio = request.form.get('domicilio')
            codigo_postal = request.form.get('codigo_postal')
            poblacion = request.form.get('poblacion')
            provincia = request.form.get('provincia')
            telefono_gestor = request.form.get('telefono_gestor')

            # Validar campos requeridos
            if not all([nombre_gestor, cif_dni, domicilio, codigo_postal, poblacion, provincia, telefono_gestor]):
                flash('Todos los campos son obligatorios', 'danger')
                return render_template('gestores/gestores/crear.html')

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
                return redirect(url_for('gestores.usuarios_gestores'))
            else:
                flash('Error al crear el gestor', 'danger')

        return render_template('usuarios_gestores/gestores/crear.html')

    except Exception as e:
        flash(f'Error al crear el gestor: {str(e)}', 'danger')
        return redirect(url_for('gestores.usuarios_gestores'))

def gestores_actualizar_vista():
    return render_template('gestores/gestores/actualizar.html')

def gestores_eliminar_vista():
    return render_template('gestores/gestores/eliminar.html')

