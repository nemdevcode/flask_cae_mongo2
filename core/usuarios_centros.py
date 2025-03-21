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
        ic("\n=== Iniciando gestores_usuarios_centros_crear_vista ===")
        
        # Obtener el ID del gestor actual
        gestor_id = session.get('usuario_id')
        ic("Gestor ID:", gestor_id)
        if not gestor_id:
            return redirect(url_for('login', mensaje_error='No hay gestor autenticado'))

        # Obtener los IDs del formulario (tanto de GET como de POST)
        titular_id = request.args.get('titular_id') or request.form.get('titular_id')
        centro_id = request.args.get('centro_id') or request.form.get('centro_id')
        ic("Titular ID recibido:", titular_id)
        ic("Centro ID recibido:", centro_id)

        if not titular_id or not centro_id:
            ic("Error: Faltan datos necesarios")
            return redirect(url_for('gestores.gestores_usuarios_centros', 
                                  mensaje_error='Faltan datos necesarios'))

        # Verificar que el centro existe
        centro = db.centros.find_one({'_id': ObjectId(centro_id)})
        ic("Centro encontrado:", centro)
        if not centro:
            ic("Error: El centro no existe")
            return redirect(url_for('gestores.gestores_usuarios_centros', 
                                  mensaje_error='El centro no existe'))

        # Obtener la información del titular
        titular = db.usuarios_titulares.find_one({'_id': ObjectId(titular_id)})
        ic("Titular encontrado:", titular)
        if not titular:
            ic("Error: El titular no existe")
            return redirect(url_for('gestores.gestores_usuarios_centros', 
                                  mensaje_error='El titular no existe'))

        titular_info = db.usuarios.find_one({'_id': titular['usuario_id']})
        ic("Información del titular:", titular_info)
        if not titular_info:
            ic("Error: No se encontró la información del titular")
            return redirect(url_for('gestores.gestores_usuarios_centros', 
                                  mensaje_error='No se encontró la información del titular'))

        if request.method == 'POST':
            ic("Método POST detectado")
            # Obtener datos del formulario
            alias = request.form.get('alias')
            nombre_usuario = request.form.get('nombre_usuario')
            telefono = request.form.get('telefono')
            email = request.form.get('email')
            password = request.form.get('password')
            estado = request.form.get('estado', 'activo')
            ic("Datos del formulario recibidos:", {
                'alias': alias,
                'nombre_usuario': nombre_usuario,
                'telefono': telefono,
                'email': email,
                'estado': estado
            })

            # Crear el usuario
            usuario_id = UsuariosCentrosCollection.crear_usuario(
                alias=alias,
                nombre_usuario=nombre_usuario,
                telefono=telefono,
                email=email,
                password=password,
                estado=estado,
                centro_id=centro_id
            )
            ic("Usuario creado con ID:", usuario_id)

            if usuario_id:
                ic("Usuario creado exitosamente")
                return redirect(url_for('gestores.gestores_usuarios_centros', 
                                     expandir_titular=titular_id,
                                     mensaje_ok='Usuario creado exitosamente'))
            else:
                ic("Error al crear el usuario")
                return redirect(url_for('gestores.gestores_usuarios_centros', 
                                     mensaje_error='Error al crear el usuario'))

        # Para GET, renderizar el formulario
        ic("Método GET detectado, renderizando template")
        return render_template('gestores/usuarios_centros/crear.html',
                             titular={
                                 '_id': titular_id,
                                 'titular_info': {
                                     'alias': titular['alias'],
                                     'estado': titular['estado']
                                 },
                                 'nombre_usuario': titular_info['nombre_usuario']
                             },
                             centro=centro)

    except Exception as e:
        ic("Error en gestores_usuarios_centros_crear_vista:", str(e))
        return redirect(url_for('gestores.gestores_usuarios_centros', 
                              mensaje_error=f'Error: {str(e)}'))

def gestores_usuarios_centros_actualizar_vista():
    return render_template('gestores/usuarios_centros/actualizar.html')

def gestores_usuarios_centros_eliminar_vista():
    return render_template('gestores/usuarios_centros/eliminar.html')