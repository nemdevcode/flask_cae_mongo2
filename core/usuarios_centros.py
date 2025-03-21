from flask import render_template, redirect, url_for, request, session
from bson import ObjectId
from datetime import datetime
from icecream import ic
ic.enable()

from models.centros_model import UsuariosCentrosCollection
from models.centros_model import CentrosCollection

from config import conexion_mongo

db = conexion_mongo()

def obtener_usuarios_centro(centro_id):
    """
    Obtiene los usuarios asociados a un centro específico
    """
    usuarios_centro = []
    query = {
        'centro_id': ObjectId(centro_id),
        'estado': 'activo'
    }
    
    for uc in db.usuarios_centros.find(query):
        # Obtener la información del usuario
        usuario = db.usuarios.find_one({'_id': uc['usuario_id']})
        if usuario:
            usuario_centro = {
                '_id': uc['_id'],
                'usuario_info': {
                    'alias': uc['alias'],
                    'estado': uc['estado']
                },
                'nombre_usuario': usuario['nombre_usuario'],
                'telefono': usuario['telefono'],
                'email': usuario['email']
            }
            usuarios_centro.append(usuario_centro)
    
    return usuarios_centro

def obtener_centros_titular(titular_id):
    """
    Obtiene los centros activos de un titular
    """
    centros = []
    
    # Primero obtener el usuario_id del titular
    titular = db.usuarios_titulares.find_one({'_id': ObjectId(titular_id)})
    if not titular:
        return centros
        
    usuario_id = titular['usuario_id']
    
    query = {
        'titular_id': usuario_id,  # Usar el usuario_id en lugar del _id de la relación
        'estado': 'activo'
    }
    
    for centro in db.centros.find(query):
        centro['_id'] = str(centro['_id'])
        centro['titular_id'] = str(centro['titular_id'])
        centros.append(centro)
    
    return centros

def gestores_usuarios_centros_vista():
    
    try:
        # Obtener el ID del gestor actual
        gestor_id = session.get('usuario_id')
        if not gestor_id:
            return redirect(url_for('login', mensaje_error='No hay gestor autenticado'))

        # Obtener el nombre del gestor
        gestor = db.usuarios.find_one({'_id': ObjectId(gestor_id)})
        nombre_gestor = gestor.get('nombre_usuario', '') if gestor else ''

        # Obtener el ID del titular a expandir
        expandir_titular = request.form.get('expandir_titular') or request.args.get('expandir_titular')

        # Obtener el filtro de titular
        filtro_titular = request.form.get('filtrar_titular', '').strip().upper()

        # Obtener titulares activos
        titulares = []
        query = {'gestor_id': ObjectId(gestor_id), 'estado': 'activo'}
        usuarios_titulares = db.usuarios_titulares.find(query)
        
        for ut in usuarios_titulares:
            usuario = db.usuarios.find_one({'_id': ut['usuario_id']})
            if usuario:
                # Si hay filtro por nombre, verificar si coincide
                if filtro_titular:
                    if (filtro_titular.lower() not in usuario['nombre_usuario'].lower() and 
                        filtro_titular.lower() not in ut['alias'].lower()):
                        continue

                titular = {
                    '_id': ut['_id'],
                    'titular_info': {
                        'alias': ut['alias'],
                        'estado': ut['estado']
                    },
                    'nombre_usuario': usuario['nombre_usuario']
                }
                titulares.append(titular)

        # Obtener centros y usuarios por titular
        centros_por_titular = {}
        usuarios_por_centro = {}
        
        for titular in titulares:
            # Obtener filtros específicos para este titular
            filtro_centro = request.form.get(f'filtrar_centro_{titular["_id"]}', '').strip().upper()
            filtro_estado = request.form.get(f'filtrar_estado_{titular["_id"]}', 'todos')

            # Obtener y filtrar centros
            centros = obtener_centros_titular(titular['_id'])
            
            # Aplicar filtro de texto si existe
            if filtro_centro:
                centros = [
                    centro for centro in centros
                    if (filtro_centro in centro['nombre_centro'].upper() or
                        filtro_centro in centro['domicilio'].upper() or
                        filtro_centro in centro['codigo_postal'].upper() or
                        filtro_centro in centro['poblacion'].upper() or
                        filtro_centro in centro['provincia'].upper())
                ]

            # Aplicar filtro de estado si no es 'todos'
            if filtro_estado != 'todos':
                centros = [centro for centro in centros if centro['estado'] == filtro_estado]

            centros_por_titular[titular['_id']] = centros

            # Obtener usuarios para cada centro
            for centro in centros:
                # Obtener filtros específicos para este centro
                filtro_usuario = request.form.get(f'filtrar_usuario_{centro["_id"]}', '').strip().lower()
                filtro_estado_usuario = request.form.get(f'filtrar_estado_usuario_{centro["_id"]}', 'todos')

                # Obtener y filtrar usuarios
                usuarios = obtener_usuarios_centro(centro['_id'])
                
                # Aplicar filtro de texto si existe
                if filtro_usuario:
                    usuarios = [
                        usuario for usuario in usuarios
                        if (filtro_usuario in usuario['nombre_usuario'].lower() or
                            filtro_usuario in usuario['usuario_info']['alias'].lower() or
                            filtro_usuario in usuario['telefono'].lower() or
                            filtro_usuario in usuario['email'].lower())
                    ]

                # Aplicar filtro de estado si no es 'todos'
                if filtro_estado_usuario != 'todos':
                    usuarios = [usuario for usuario in usuarios if usuario['usuario_info']['estado'] == filtro_estado_usuario]

                usuarios_por_centro[centro['_id']] = usuarios

        # Obtener mensajes de la URL
        mensaje_ok = request.args.get('mensaje_ok', '')
        mensaje_error = request.args.get('mensaje_error', '')

        return render_template('gestores/usuarios_centros/listar.html',
                             nombre_gestor=nombre_gestor,
                             titulares=titulares,
                             centros_por_titular=centros_por_titular,
                             usuarios_por_centro=usuarios_por_centro,
                             expandir_titular=expandir_titular,
                             mensaje_ok=mensaje_ok,
                             mensaje_error=mensaje_error)
                             
    except Exception as e:
        return redirect(url_for('gestores.gestores_usuarios_centros', 
                              mensaje_error=f'Error al cargar los usuarios de centros: {str(e)}'))

def gestores_usuarios_centros_crear_vista():
    
    try:
        # Obtener el ID del gestor actual
        gestor_id = session.get('usuario_id')
        if not gestor_id:
            return redirect(url_for('login', mensaje_error='No hay gestor autenticado'))

        # Obtener el nombre del gestor
        gestor = db.usuarios.find_one({'_id': ObjectId(gestor_id)})
        nombre_gestor = gestor.get('nombre_usuario', '') if gestor else ''

        # Obtener el ID del titular y centro
        titular_id = request.args.get('titular_id')
        centro_id = request.args.get('centro_id')
        if not titular_id or not centro_id:
            return redirect(url_for('gestores.gestores_usuarios_centros', 
                                  mensaje_error='ID de titular o centro no proporcionado'))

        # Verificar que el titular pertenece al gestor actual
        titular = db.usuarios_titulares.find_one({
            '_id': ObjectId(titular_id),
            'gestor_id': ObjectId(gestor_id)
        })

        if not titular:
            return redirect(url_for('gestores.gestores_usuarios_centros', 
                                  mensaje_error='Titular no encontrado o no pertenece a este gestor'))

        # Obtener la información del usuario titular
        titular_info = db.usuarios.find_one({'_id': titular['usuario_id']})
        if not titular_info:
            return redirect(url_for('gestores.gestores_usuarios_centros', 
                                  mensaje_error='No se encontró la información del titular'))

        # Formatear los datos del titular para el template
        titular_formateado = {
            '_id': titular['_id'],
            'titular_info': {
                'alias': titular['alias'],
                'estado': titular['estado']
            },
            'nombre_usuario': titular_info['nombre_usuario']
        }

        # Verificar que el centro existe
        centro = db.centros.find_one({'_id': ObjectId(centro_id)})
        if not centro:
            return redirect(url_for('gestores.gestores_usuarios_centros', 
                                  mensaje_error='Centro no encontrado'))

        if request.method == 'GET':
            return render_template('gestores/usuarios_centros/crear.html', 
                                 titular=titular_formateado,
                                 centro=centro,
                                 nombre_gestor=nombre_gestor)

        if request.method == 'POST':
            # Obtener datos del formulario
            alias = request.form.get('alias', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '').strip()
            password_confirmacion = request.form.get('password_confirmacion', '').strip()

            if password != password_confirmacion:
                return render_template('gestores/usuarios_centros/crear.html',
                                    titular=titular_formateado,
                                    centro=centro,
                                    nombre_gestor=nombre_gestor,
                                    mensaje_error='Las contraseñas no coinciden',
                                    form_data=request.form)

            # Verificar si el alias ya existe para este centro
            if db.usuarios_centros.find_one({
                'alias': alias,
                'centro_id': ObjectId(centro_id)
            }):
                return render_template('gestores/usuarios_centros/crear.html',
                                    titular=titular_formateado,
                                    centro=centro,
                                    nombre_gestor=nombre_gestor,
                                    mensaje_error='El alias ya está en uso para este centro',
                                    form_data=request.form)

            # Verificar si ya existe un usuario con ese email
            usuario_existente = db.usuarios.find_one({'email': email})
            if usuario_existente:
                # Verificar si ya es usuario de este centro
                usuario_centro_existente = db.usuarios_centros.find_one({
                    'usuario_id': usuario_existente['_id'],
                    'centro_id': ObjectId(centro_id)
                })
                if usuario_centro_existente:
                    return render_template('gestores/usuarios_centros/crear.html',
                                        titular=titular_formateado,
                                        centro=centro,
                                        nombre_gestor=nombre_gestor,
                                        mensaje_error='Este usuario ya es usuario de este centro',
                                        form_data=request.form)
                
                # Usar el usuario existente
                usuario_id = usuario_existente['_id']
            else:
                # Crear nuevo usuario
                usuario_data = {
                    'nombre_usuario': '',
                    'email': email,
                    'password': password,
                    'telefono': '',
                    'fecha_alta': datetime.now(),
                    'fecha_modificacion': datetime.now(),
                    'fecha_baja': None,
                    'estado': 'activo'
                }
                resultado_usuario = db.usuarios.insert_one(usuario_data)
                usuario_id = resultado_usuario.inserted_id

                # Obtener o crear el rol de usuario_centro
                rol_usuario_centro = db.roles.find_one({'nombre_rol': 'centro'})
                if not rol_usuario_centro:
                    rol_data = {
                        'nombre_rol': 'centro',
                        'descripcion': 'Rol de usuario de centro',
                        'fecha_alta': datetime.now(),
                        'fecha_modificacion': datetime.now(),
                        'fecha_baja': None,
                        'estado': 'activo'
                    }
                    resultado_rol = db.roles.insert_one(rol_data)
                    rol_id = resultado_rol.inserted_id
                else:
                    rol_id = rol_usuario_centro['_id']

                # Crear la relación usuario-rol
                usuario_rol_data = {
                    'usuario_id': usuario_id,
                    'rol_id': rol_id,
                    'fecha_alta': datetime.now(),
                    'fecha_modificacion': datetime.now(),
                    'fecha_baja': None,
                    'estado': 'activo'
                }
                db.usuarios_roles.insert_one(usuario_rol_data)
            
            # Crear el usuario de centro
            usuario_centro_data = {
                'usuario_id': usuario_id,
                'centro_id': ObjectId(centro_id),
                'alias': alias,
                'estado': 'activo',
                'fecha_alta': datetime.now(),
                'fecha_modificacion': datetime.now(),
                'fecha_baja': None
            }
            
            # Insertar usuario de centro
            db.usuarios_centros.insert_one(usuario_centro_data)
            
            # Redireccionar con mensaje de éxito
            return redirect(url_for('gestores.gestores_usuarios_centros', 
                                  mensaje_ok='Usuario de centro creado exitosamente'))
            
    except Exception as e:
        return render_template('gestores/usuarios_centros/crear.html',
                             titular=titular_formateado if 'titular_formateado' in locals() else None,
                             centro=centro if 'centro' in locals() else None,
                             nombre_gestor=nombre_gestor if 'nombre_gestor' in locals() else None,
                             mensaje_error=str(e),
                             form_data=request.form if 'request' in locals() else None)

def gestores_usuarios_centros_actualizar_vista():
    return render_template('gestores/usuarios_centros/actualizar.html')

def gestores_usuarios_centros_eliminar_vista():
    return render_template('gestores/usuarios_centros/eliminar.html')