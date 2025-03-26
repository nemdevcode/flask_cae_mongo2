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
                    if (filtrar_cogestor.lower() not in uc['alias'].lower() and
                        filtrar_cogestor.lower() not in usuario['email'].lower()):
                        continue

                cogestor = {
                    '_id': uc['_id'],
                    'cogestor_info': {
                        'alias': uc['alias'],
                        'nombre_usuario': usuario['nombre_usuario'],
                        'telefono': usuario['telefono'],
                        'estado': uc['estado']
                    },
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

def obtener_rol_cogestor():
    
    """Obtiene el rol de cogestor, lo crea si no existe"""
    rol_cogestor = db.roles.find_one({'nombre_rol': 'cogestor'})
    if not rol_cogestor:
        rol_data = {
            'nombre_rol': 'cogestor',
            'descripcion': 'Rol de cogestor',
            'fecha_alta': datetime.now(),
            'fecha_modificacion': datetime.now(),
            'fecha_baja': None,
            'estado': 'activo'
        }
        resultado_rol = db.roles.insert_one(rol_data)
        return resultado_rol.inserted_id
    return rol_cogestor['_id']

def obtener_usuario_rol(usuario_id, rol_id):

    """Obtiene el usuario_rol, lo crea si no existe"""
    usuario_rol_existente = db.usuarios_roles.find_one({
        'usuario_id': usuario_id,
        'rol_id': rol_id
    })
    
    if not usuario_rol_existente:
        usuario_rol_data = {
            'usuario_id': usuario_id,
            'rol_id': rol_id,
            'fecha_alta': datetime.now(),
            'fecha_modificacion': datetime.now(),
            'fecha_baja': None,
            'estado': 'activo'
        }
        resultado_usuario_rol = db.usuarios_roles.insert_one(usuario_rol_data)
        return resultado_usuario_rol.inserted_id
    return usuario_rol_existente['_id']

def crear_usuario_cogestor(usuario_rol_id, gestor_id, alias):

    """Crea un nuevo usuario_cogestor"""
    return db.usuarios_cogestores.insert_one({
        'usuario_rol_id': usuario_rol_id,
        'gestor_id': ObjectId(gestor_id),
        'alias': alias,
        'estado': 'activo',
        'fecha_creacion': datetime.now(),
        'fecha_modificacion': datetime.now()
    })

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
            alias = request.form.get('alias', '').strip().upper()
            email = request.form.get('email', '').strip().lower()

            # Verificar si el email existe en la colección usuarios
            usuario_existente = db.usuarios.find_one({'email': email})
            
            if usuario_existente:
                # Si existe el usuario, verificar si ya es cogestor para este gestor
                usuario_id = usuario_existente['_id']
                cogestor_existente = db.usuarios_cogestores.find_one({
                    'usuario_id': usuario_id,
                    'gestor_id': ObjectId(gestor_id)
                })
                
                if cogestor_existente:
                    flash('Este email ya está registrado como cogestor para este gestor', 'danger')
                    return render_template('gestores/usuarios_cogestores/crear.html',
                                        form_data=request.form)
                
                # Obtener rol de cogestor y crear usuario_rol
                rol_id = obtener_rol_cogestor()
                usuario_rol_id = obtener_usuario_rol(usuario_id, rol_id)
                
                # Crear el cogestor
                crear_usuario_cogestor(usuario_rol_id, gestor_id, alias)
                flash('Cogestor creado correctamente', 'success')
                return redirect(url_for('gestores.gestores_usuarios_cogestores'))

            # Si el usuario no existe, crear nuevo usuario y cogestor
            # Generar token de verificación
            token = generar_token_verificacion(email)

            # Crear el usuario
            usuario_id = db.usuarios.insert_one({
                'email': email,
                'estado': 'pendiente',
                'verificado': False,
                'token_verificacion': token,
                'fecha_creacion': datetime.now(),
                'fecha_modificacion': datetime.now()
            }).inserted_id

            # Obtener rol de cogestor y crear usuario_rol
            rol_id = obtener_rol_cogestor()
            usuario_rol_id = obtener_usuario_rol(usuario_id, rol_id)
            
            # Crear el cogestor
            crear_usuario_cogestor(usuario_rol_id, gestor_id, alias)

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
            'email': usuario['email']
        }

        if request.method == 'GET':
            return render_template('gestores/usuarios_cogestores/actualizar.html', cogestor=cogestor_data)

        if request.method == 'POST':
            # Obtener datos del formulario
            alias = request.form.get('alias', '').strip().upper()
            estado = request.form.get('estado', 'activo')

            # Verificar si el alias ya existe para este gestor (excluyendo el cogestor actual)
            if db.usuarios_cogestores.find_one({
                'alias': alias,
                'gestor_id': ObjectId(gestor_id),
                '_id': {'$ne': ObjectId(cogestor_id)}
            }):
                flash('El alias ya está en uso para este gestor', 'danger')
                return render_template('gestores/usuarios_cogestores/actualizar.html',
                                    cogestor=cogestor_data)

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


