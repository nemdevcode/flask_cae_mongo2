from flask import render_template, request, redirect, url_for, session, flash
from bson import ObjectId
from datetime import datetime
from config import conexion_mongo
from utils.token_utils import generar_token_verificacion
from utils.email_utils import enviar_email

db = conexion_mongo()

def gestores_usuarios_cogestores_vista():
    
    try:
        # Obtener el ID del gestor actual desde la sesión
        gestor_id = session.get('usuario_id')
        if not gestor_id:
            flash('No hay gestor autenticado', 'danger')
            return redirect(url_for('login'))

        # Obtener el nombre del gestor
        gestor = db.usuarios.find_one({'_id': ObjectId(gestor_id)})
        nombre_gestor = gestor.get('nombre_usuario', 'Gestor')

        # Obtener parámetros de filtrado
        filtrar_cogestor = request.form.get('filtrar_cogestor', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')

        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('gestores.gestores_usuarios_cogestores'))

        # Construir la consulta base
        query = {'gestor_id': ObjectId(gestor_id)}
        
        # Aplicar filtros si existen
        if filtrar_estado != 'todos':
            query['estado'] = filtrar_estado

        # Obtener los cogestores asociados al gestor
        cogestores = []
        usuarios_cogestores = db.usuarios_cogestores.find(query)
        
        for uc in usuarios_cogestores:
            # Obtener la información del usuario
            usuario = db.usuarios.find_one({'_id': uc['usuario_id']})
            if usuario:
                # Si hay filtro por nombre, verificar si coincide
                if filtrar_cogestor:
                    if (filtrar_cogestor.lower() not in usuario['nombre_usuario'].lower() and 
                        filtrar_cogestor.lower() not in uc['alias'].lower() and
                        filtrar_cogestor.lower() not in usuario['telefono'].lower() and
                        filtrar_cogestor.lower() not in usuario['email'].lower()):
                        continue

                cogestor = {
                    '_id': uc['_id'],
                    'cogestor_info': {
                        'alias': uc['alias'],
                        'estado': uc['estado']
                    },
                    'nombre_usuario': usuario['nombre_usuario'],
                    'telefono': usuario['telefono'],
                    'email': usuario['email']
                }
                cogestores.append(cogestor)

                # Obtener mensaje_ok de los argumentos de la URL si existe
                # mensaje_ok = request.args.get('mensaje_ok')

        return render_template('gestores/usuarios_cogestores/listar.html', 
                             cogestores=cogestores,
                             nombre_gestor=nombre_gestor,
                             filtrar_cogestor=filtrar_cogestor,
                             filtrar_estado=filtrar_estado,
                            #  mensaje_ok=mensaje_ok,
                             )
    except Exception as e:
        flash(f'Error al listar los cogestores: {str(e)}', 'danger')
        return redirect(url_for('gestores.gestores_usuarios_cogestores'))

def gestores_usuarios_cogestores_crear_vista():
    if request.method == 'GET':
        return render_template('gestores/usuarios_cogestores/crear.html')
    
    if request.method == 'POST':
        try:
            # Obtener el ID del gestor actual
            gestor_id = session.get('usuario_id')
            if not gestor_id:
                flash('No hay gestor autenticado', 'danger')
                return redirect(url_for('login'))

            # Obtener datos del formulario
            alias = request.form.get('alias', '').strip()
            email = request.form.get('email', '').strip().lower()
            nombre_usuario = request.form.get('nombre_usuario', '').strip()
            telefono = request.form.get('telefono', '').strip()

            # Validaciones básicas
            if not all([alias, email, nombre_usuario, telefono]):
                flash('Todos los campos son obligatorios', 'danger')
                return render_template('gestores/usuarios_cogestores/crear.html',
                                    form_data=request.form)

            # Verificar si el email ya existe
            if db.usuarios.find_one({'email': email}):
                flash('El email ya está registrado', 'danger')
                return render_template('gestores/usuarios_cogestores/crear.html',
                                    form_data=request.form)

            # Generar token de verificación
            token = generar_token_verificacion(email)

            # Crear el usuario
            usuario_id = db.usuarios.insert_one({
                'nombre_usuario': nombre_usuario,
                'email': email,
                'telefono': telefono,
                'estado': 'pendiente',
                'verificado': False,
                'token_verificacion': token,
                'fecha_creacion': datetime.now(),
                'fecha_modificacion': datetime.now()
            }).inserted_id

            # Crear el cogestor
            db.usuarios_cogestores.insert_one({
                'usuario_id': usuario_id,
                'gestor_id': ObjectId(gestor_id),
                'alias': alias,
                'estado': 'pendiente',
                'fecha_creacion': datetime.now(),
                'fecha_modificacion': datetime.now()
            })

            # Enviar email de verificación
            link_verificacion = url_for('verificar_email', token=token, email=email, _external=True)
            cuerpo_email = f"""
            <h2>Bienvenido a CAE Accesible</h2>
            <p>Has sido registrado como cogestor en CAE Accesible. Para activar tu cuenta, haz clic en el siguiente enlace:</p>
            <p><a href="{link_verificacion}">Activar cuenta</a></p>
            <p>Este enlace expirará en 1 hora.</p>
            <p>Si no solicitaste este registro, puedes ignorar este correo.</p>
            """

            if enviar_email(email, "Activación de cuenta - CAE Accesible", cuerpo_email):
                flash('Cogestor creado correctamente. Se ha enviado un email de activación.', 'success')
            else:
                flash('Cogestor creado pero hubo un error al enviar el email de activación.', 'warning')

            return redirect(url_for('gestores.gestores_usuarios_cogestores'))

        except Exception as e:
            flash(f'Error al crear el cogestor: {str(e)}', 'danger')
            return render_template('gestores/usuarios_cogestores/crear.html',
                                form_data=request.form)

def gestores_usuarios_cogestores_actualizar_vista():
    
    try:
        # Obtener el ID del gestor actual
        gestor_id = session.get('usuario_id')
        if not gestor_id:
            flash('No hay gestor autenticado', 'danger')
            return redirect(url_for('login'))

        # Obtener el ID del cogestor a actualizar
        cogestor_id = request.args.get('cogestor_id')
        if not cogestor_id:
            flash('ID de cogestor no proporcionado', 'danger')
            return redirect(url_for('gestores.gestores_usuarios_cogestores'))

        # Verificar que el cogestor pertenece al gestor actual
        cogestor = db.usuarios_cogestores.find_one({
            '_id': ObjectId(cogestor_id),
            'gestor_id': ObjectId(gestor_id)
        })

        if not cogestor:
            flash('Cogestor no encontrado o no pertenece a este gestor', 'danger')
            return redirect(url_for('gestores.gestores_usuarios_cogestores'))

        # Obtener la información del usuario
        usuario = db.usuarios.find_one({'_id': cogestor['usuario_id']})
        if not usuario:
            flash('Usuario no encontrado', 'danger')
            return redirect(url_for('gestores.gestores_usuarios_cogestores'))

        # Preparar los datos para el template
        cogestor_data = {
            '_id': cogestor['_id'],
            'cogestor_info': {
                'alias': cogestor['alias'],
                'estado': cogestor['estado']
            },
            'email': usuario['email'],
            'password': usuario['password']
        }

        if request.method == 'GET':
            return render_template('gestores/usuarios_cogestores/actualizar.html', cogestor=cogestor_data)

        if request.method == 'POST':
            # Obtener datos del formulario
            alias = request.form.get('alias', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '').strip()
            password_confirm = request.form.get('password_confirm', '').strip()
            estado = request.form.get('estado', 'activo')

            if password != password_confirm:
                flash('Las contraseñas no coinciden', 'danger')
                return render_template('gestores/usuarios_cogestores/actualizar.html',
                                        cogestor=cogestor_data)

            # Verificar si el alias ya existe para este gestor (excluyendo el cogestor actual)
            if db.usuarios_cogestores.find_one({
                'alias': alias,
                'gestor_id': ObjectId(gestor_id),
                '_id': {'$ne': ObjectId(cogestor_id)}
            }):
                flash('El alias ya está en uso para este gestor', 'danger')
                return render_template('gestores/usuarios_cogestores/actualizar.html',
                                        cogestor=cogestor_data)

            # Verificar si el email ya existe en otro usuario
            if email != usuario['email']:
                if db.usuarios.find_one({'email': email}):
                    flash('El email ya está en uso por otro usuario', 'danger')
                    return render_template('gestores/usuarios_cogestores/actualizar.html',
                                        cogestor=cogestor_data)

            # Actualizar el usuario
            db.usuarios.update_one(
                {'_id': usuario['_id']},
                {
                    '$set': {
                        'email': email,
                        'fecha_modificacion': datetime.now()
                    }
                }
            )

            # Actualizar el cogestor
            db.usuarios_cogestores.update_one(
                {'_id': ObjectId(cogestor_id)},
                {
                    '$set': {
                        'alias': alias,
                        'estado': estado,
                        'fecha_modificacion': datetime.now()
                    }
                }
            )

            flash('Cogestor actualizado exitosamente', 'success')
            return redirect(url_for('gestores.gestores_usuarios_cogestores'))

    except Exception as e:
        flash(f'Error al actualizar el cogestor: {str(e)}', 'danger')
        return render_template('gestores/usuarios_cogestores/actualizar.html',
                             cogestor=cogestor_data if 'cogestor_data' in locals() else None)

def gestores_usuarios_cogestores_eliminar_vista():
    try:
        # Obtener el ID del gestor actual
        gestor_id = session.get('usuario_id')
        if not gestor_id:
            flash('No hay gestor autenticado', 'danger')
            return redirect(url_for('login'))

        # Obtener el ID del cogestor a eliminar
        cogestor_id = request.args.get('cogestor_id')
        if not cogestor_id:
            flash('ID de cogestor no proporcionado', 'danger')
            return redirect(url_for('gestores.gestores_usuarios_cogestores'))

        # Verificar que el cogestor pertenece al gestor actual
        cogestor = db.usuarios_cogestores.find_one({
            '_id': ObjectId(cogestor_id),
            'gestor_id': ObjectId(gestor_id)
        })

        if not cogestor:
            flash('Cogestor no encontrado o no pertenece a este gestor', 'danger')
            return redirect(url_for('gestores.gestores_usuarios_cogestores'))

        # Eliminar el cogestor
        db.usuarios_cogestores.delete_one({'_id': ObjectId(cogestor_id)})
        flash('Cogestor eliminado exitosamente', 'success')
        return redirect(url_for('gestores.gestores_usuarios_cogestores'))

    except Exception as e:
        flash(f'Error al eliminar el cogestor: {str(e)}', 'danger')
        return redirect(url_for('gestores.gestores_usuarios_cogestores'))

def usuarios_cogestores_vista():
    return render_template('cogestores/cogestores.html')

def usuarios_cogestores_gestor_vista():
    return render_template('cogestores/cogestores_gestor.html')


