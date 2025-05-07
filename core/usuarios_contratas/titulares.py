from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from utils.usuario_utils import obtener_usuario_autenticado
from utils.rol_utils import verificar_rol_contrata
from config import conexion_mongo

db = conexion_mongo()

def titulares_vista(usuario_rol_contrata_id, contrata_id):
    '''
    Vista de usuarios de contratas para ver los titulares asignados a la contrata.
    '''
    # Obtener parámetros de filtrado
    filtrar_titular = request.form.get('filtrar_titular', '')
    vaciar = request.args.get('vaciar', '0')
    
    # Si se solicita vaciar filtros
    if vaciar == '1':
        return redirect(url_for('ucon_titulares.titulares', 
                                usuario_rol_contrata_id=usuario_rol_contrata_id,
                                contrata_id=contrata_id))
    
    # Obtener el titular_id de la contrata
    titular_id = db.contratas.find_one(
        {'contrata_id': ObjectId(contrata_id)}, 
        {'titular_id': 1}
        )



    # Obtener titulares
    titulares = []
    titulares = list(db.titulares.find_one({'_id': ObjectId(titular_id)}))

    for titular_id in titulares_ids:
        titular = db.titulares.find_one({'_id': ObjectId(titular_id)})
        if titular:
            if filtrar_titular:
                if (filtrar_titular.lower() not in titular['nombre_titular'].lower() and
                    filtrar_titular.lower() not in titular['cif_dni'].lower() and
                    filtrar_titular.lower() not in titular['domicilio'].lower() and
                    filtrar_titular.lower() not in titular['codigo_postal'].lower() and
                    filtrar_titular.lower() not in titular['poblacion'].lower() and
                    filtrar_titular.lower() not in titular['provincia'].lower() and
                    filtrar_titular.lower() not in titular['telefono_titular'].lower()):
                    continue

            titulares.append(
                {
                    'titular_id': str(titular['_id']),
                    'nombre_titular': titular['nombre_titular'],
                    'cif_dni': titular['cif_dni'],
                    'domicilio': titular['domicilio'],
                    'codigo_postal': titular['codigo_postal'],
                    'poblacion': titular['poblacion'],
                    'provincia': titular['provincia'],
                    'telefono_titular': titular['telefono_titular']
                }
            )

    # Obtener nombre de la contrata
    nombre_contrata = db.contratas.find_one({'_id': ObjectId(contrata_id)})['nombre_contrata']

    return render_template('usuarios_contratas/titulares/listar.html',
                           usuario_rol_contrata_id=usuario_rol_contrata_id,
                           contrata_id=contrata_id,
                           titulares=titulares,
                           nombre_contrata=nombre_contrata
                           )

def titulares_titular_vista(usuario_rol_contrata_id, contrata_id, titular_id):
    '''
    Vista de usuarios de contratas para ver los titulares asignados a la contrata.
    '''
    return render_template('usuarios_contratas/titulares/index.html',
                           usuario_rol_contrata_id=usuario_rol_contrata_id,
                           contrata_id=contrata_id,
                           titular_id=titular_id
                           )