from flask import render_template, request, redirect, url_for, session, flash
from bson import ObjectId
from datetime import datetime
from config import conexion_mongo
from utils.token_utils import generar_token_verificacion
from utils.email_utils import enviar_email
from utils.usuario_rol_utils import (
    crear_rol,
    crear_usuario_rol,
    verificar_usuario_existente,
    crear_usuario,
    obtener_rol,
    obtener_usuario_rol
)
from models.usuarios_model import UsuariosCollection
from models.roles_model import RolesCollection
from models.usuarios_roles_model import UsuariosRolesCollection
from icecream import ic

db = conexion_mongo()

def gestores_usuarios_cogestores_vista():
    try:
        # Obtener el ID del usuario actual
        usuario_id = session.get('usuario_id')
        ic("usuario_id:", usuario_id)
        
        if not usuario_id:
            flash('No hay usuario autenticado', 'danger')
            return redirect(url_for('login'))

        # Obtener el rol de gestor
        existe_rol, rol_gestor_id = obtener_rol('gestor')
        ic("existe_rol:", existe_rol, "rol_gestor_id:", rol_gestor_id)
        
        if not existe_rol:
            flash('Rol de gestor no encontrado', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        # Verificar si el usuario tiene el rol de gestor
        tiene_rol, usuario_rol_id = obtener_usuario_rol(usuario_id, rol_gestor_id)
        ic("tiene_rol:", tiene_rol, "usuario_rol_id:", usuario_rol_id)
        
        if not tiene_rol:
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('usuarios.usuarios'))

        # Obtener la información del usuario
        usuario = db.usuarios.find_one({'_id': ObjectId(usuario_id)})
        ic("usuario:", usuario)
        
        nombre_gestor = usuario.get('nombre_usuario', 'Gestor')

        # Obtener parámetros de filtrado
        filtrar_cogestor = request.form.get('filtrar_cogestor', '')
        filtrar_estado = request.form.get('filtrar_estado', 'todos')
        vaciar = request.args.get('vaciar', '0')
        ic("filtros:", {"filtrar_cogestor": filtrar_cogestor, "filtrar_estado": filtrar_estado, "vaciar": vaciar})

        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('gestores.gestores_usuarios_cogestores'))

        # Construir la consulta base
        query = {'usuario_rol_id': usuario_rol_id}
        ic("query base:", query)
        
        # Aplicar filtros si existen
        if filtrar_estado != 'todos':
            query['estado_usuario_cogestor'] = filtrar_estado
        ic("query final:", query)

        # Obtener los cogestores asociados al gestor
        cogestores = []
        usuarios_cogestores = list(db.usuarios_cogestores.find(query))
        ic("usuarios_cogestores encontrados:", len(usuarios_cogestores))
        
        for uc in usuarios_cogestores:
            ic("procesando cogestor:", uc)
            # Obtener la información del usuario cogestor
            usuario_cogestor = db.usuarios.find_one({'_id': uc['usuario_id']})
            ic("usuario_cogestor encontrado:", usuario_cogestor)
            
            if usuario_cogestor:
                # Si hay filtro por nombre, verificar si coincide
                if filtrar_cogestor:
                    if (filtrar_cogestor.lower() not in uc['alias_usuario_cogestor'].lower() and
                        filtrar_cogestor.lower() not in usuario_cogestor['email'].lower()):
                        continue

                cogestor = {
                    '_id': uc['_id'],
                    'cogestor_info': {
                        'alias': uc['alias_usuario_cogestor'],
                        'nombre_usuario': usuario_cogestor['nombre_usuario'],
                        'telefono': usuario_cogestor['telefono'],
                        'estado': uc['estado_usuario_cogestor']
                    },
                    'email': usuario_cogestor['email']
                }
                cogestores.append(cogestor)
                ic("cogestor procesado:", cogestor)

        ic("total cogestores procesados:", len(cogestores))
        ic("template a renderizar:", 'usuarios_gestores/usuarios_cogestores/listar.html')

        return render_template('usuarios_gestores/usuarios_cogestores/listar.html', 
                             cogestores=cogestores,
                             nombre_gestor=nombre_gestor,
                             filtrar_cogestor=filtrar_cogestor,
                             filtrar_estado=filtrar_estado)

    except Exception as e:
        ic("Error en gestores_usuarios_cogestores_vista:", str(e))
        flash(f'Error al listar los cogestores: {str(e)}', 'danger')
        return redirect(url_for('usuarios.usuarios'))

def crear_usuario_cogestor(usuario_rol_id, gestor_id, alias):
    """
    Crea un nuevo usuario cogestor
    """
    fecha_actual = datetime.now()
    usuario_cogestor = {
        'usuario_rol_id': usuario_rol_id,
        'gestor_id': gestor_id,
        'alias_usuario_cogestor': alias,
        'fecha_activacion': fecha_actual,
        'fecha_modificacion': fecha_actual,
        'fecha_inactivacion': None,
        'estado_usuario_cogestor': 'activo'
    }
    return db.usuarios_cogestores.insert_one(usuario_cogestor)

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

            # Verificar si el usuario existe
            existe_usuario, usuario_id = verificar_usuario_existente(email)
            
            if existe_usuario:
                # Si existe el usuario, verificar si ya es cogestor para este gestor
                cogestor_existente = db.usuarios_cogestores.find_one({
                    'usuario_id': usuario_id,
                    'gestor_id': ObjectId(gestor_id)
                })
                
                if cogestor_existente:
                    flash('Este email ya está registrado como cogestor para este gestor', 'danger')
                    return render_template('gestores/usuarios_cogestores/crear.html',
                                        form_data=request.form)
                
                # Obtener rol de cogestor y crear usuario_rol
                existe_rol, rol_id = obtener_rol('cogestor')
                if not existe_rol:
                    rol_id = crear_rol('cogestor')
                
                tiene_rol, usuario_rol_id = obtener_usuario_rol(usuario_id, rol_id)
                
                if not tiene_rol:
                    usuario_rol_id = crear_usuario_rol(usuario_id, rol_id)
                
                # Obtener datos del formulario
                alias = request.form.get('alias', '').strip().upper()
                email = request.form.get('email', '').strip().lower()
                # Crear el cogestor
                crear_usuario_cogestor(usuario_rol_id, gestor_id, alias)
                flash('Cogestor creado correctamente', 'success')
                return redirect(url_for('gestores.gestores_usuarios_cogestores'))

            # Si el usuario no existe, crear nuevo usuario y cogestor
            # Generar token de verificación
            token = generar_token_verificacion(email)
            
            # Crear diccionario con los datos del nuevo usuario
            datos_usuario = {
                'token_verificacion': token,
                'estado': 'pendiente',
                'verificado': False
            }
            
            # Crear el nuevo usuario
            usuario_id = crear_usuario(email, datos_usuario)
            
            # Obtener rol de cogestor y crear usuario_rol
            existe_rol, rol_id = obtener_rol('cogestor')
            if not existe_rol:
                rol_id = crear_rol('cogestor')
            
            usuario_rol_id = crear_usuario_rol(usuario_id, rol_id)
            
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


