from flask import render_template, session, request, redirect, url_for, flash, jsonify
from bson.objectid import ObjectId

from datetime import datetime

from config import conexion_mongo

db = conexion_mongo()

def obtener_titulares_activos(gestor_id):

    """Obtiene los titulares activos para un gestor específico"""
    titulares = list(db.usuarios.aggregate([
        {
            "$match": {
                "_id": {"$in": [ObjectId(rel['usuario_id']) for rel in db.usuarios_titulares.find({"gestor_id": ObjectId(gestor_id), "estado": "activo"})]}
            }
        },
        {
            "$lookup": {
                "from": "usuarios_titulares",
                "localField": "_id",
                "foreignField": "usuario_id",
                "as": "titular_info"
            }
        },
        {
            "$unwind": {
                "path": "$titular_info",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$match": {
                "titular_info.gestor_id": ObjectId(gestor_id),
                "titular_info.estado": "activo"
            }
        },
        {
            "$project": {
                "_id": 1,
                "nombre": "$nombre_usuario",
                "alias": "$titular_info.alias"
            }
        },
        {
            "$sort": {
                "alias": 1
            }
        }
    ]))
    
    # Convertir ObjectId a string para cada titular
    for titular in titulares:
        titular['_id'] = str(titular['_id'])
    
    return titulares

def obtener_centros(titular_id):
    
    """Obtiene los centros activos para un titular específico"""
    centros = list(db.centros.find({"titular_id": ObjectId(titular_id)}))
    # Convertir ObjectId a string para cada centro
    for centro in centros:
        centro['_id'] = str(centro['_id'])
        centro['titular_id'] = str(centro['titular_id'])
    return centros

def gestores_centros_vista():
    try:
        # Obtener el ID del gestor actual
        gestor_id = session.get('usuario_id')
        if not gestor_id:
            return redirect(url_for('login', mensaje_error='No hay gestor autenticado'))

        # Obtener el nombre del gestor
        gestor = db.usuarios.find_one({'_id': ObjectId(gestor_id)})
        nombre_gestor = gestor.get('nombre_usuario', 'Gestor')

        # Obtener titulares activos
        titulares = obtener_titulares_activos(gestor_id)
        
        # Crear un diccionario de centros por titular
        centros_por_titular = {}
        for titular in titulares:
            centros = obtener_centros(titular['_id'])
            # Filtrar centros si hay un término de búsqueda
            filtro_centro = request.form.get(f'filtrar_centro_{titular["_id"]}', '').strip().lower()
            filtro_estado = request.form.get(f'filtrar_estado_{titular["_id"]}', 'todos')
            
            if filtro_centro or filtro_estado != 'todos':
                centros_filtrados = []
                for centro in centros:
                    # Aplicar filtro de búsqueda
                    if filtro_centro and not any(filtro_centro in str(valor).lower() for valor in [
                        centro['nombre_centro'],
                        centro['domicilio'],
                        centro['codigo_postal'],
                        centro['poblacion'],
                        centro['provincia']
                    ]):
                        continue
                    
                    # Aplicar filtro de estado
                    if filtro_estado != 'todos' and centro['estado'] != filtro_estado:
                        continue
                        
                    centros_filtrados.append(centro)
                centros_por_titular[str(titular['_id'])] = centros_filtrados
            else:
                centros_por_titular[str(titular['_id'])] = centros

         # Obtener el ID del titular a expandir (tanto de GET como de POST)
        expandir_titular = request.args.get('expandir_titular') or request.form.get('expandir_titular', '')
        
        # Obtener mensajes de la URL si existen
        mensaje_ok = request.args.get('mensaje_ok')
        mensaje_error = request.args.get('mensaje_error')
        
        return render_template('gestores/centros/listar.html', 
                             nombre_gestor=nombre_gestor, 
                             titulares=titulares, 
                             centros_por_titular=centros_por_titular,
                             filtro_centro=filtro_centro if 'filtro_centro' in locals() else '',
                             expandir_titular=expandir_titular,
                             mensaje_ok=mensaje_ok,
                             mensaje_error=mensaje_error)
                             
    except Exception as e:
        return redirect(url_for('gestores.gestores_centros', 
                              mensaje_error=f'Error al cargar los centros: {str(e)}'))

def gestores_centros_crear_vista():
    return render_template('gestores/centros/crear.html')

def gestores_centros_actualizar_vista():
    return render_template('gestores/centros/actualizar.html')

def gestores_centros_eliminar_vista():
    return render_template('gestores/centros/eliminar.html')