from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from utils.usuario_utils import obtener_usuario_autenticado
from utils.rol_utils import verificar_rol_contrata
from config import conexion_mongo

db = conexion_mongo()

def verificaciones_consultas():
    '''
    Verifica si el usuario de contrata tiene permisos para acceder a la vista.
    Retorna:
        - (False, respuesta_redireccion) si hay algún error
        - (True, (usuario, usuario_rol_contrata_id)) si todo está correcto
    '''
    # Obtener usuario autenticado y verificar permisos
    usuario, respuesta_redireccion = obtener_usuario_autenticado()
    if respuesta_redireccion:
        return False, respuesta_redireccion

    # Verificar rol de cogestor
    tiene_rol, usuario_rol_contrata_id = verificar_rol_contrata(usuario['_id'])
    if not tiene_rol:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return False, redirect(url_for('usuarios.usuarios'))

    return True, (usuario, usuario_rol_contrata_id)

def usuarios_contratas_vista():
    '''
    Vista de inicio de usuarios de contratas, muestra las contratas asignadas al usuario.
    '''
    try:
        # Verificar permisos y obtener información
        permisos_ok, resultado = verificaciones_consultas()
        if not permisos_ok:
            return resultado
        
        usuario, usuario_rol_contrata_id = resultado

        # Obtener parámetros de filtrado
        filtrar_contrata = request.form.get('filtrar_contrata', '')
        vaciar = request.args.get('vaciar', '0')
        
        # Si se solicita vaciar filtros
        if vaciar == '1':
            return redirect(url_for('usuarios_contratas.usuarios_contratas'))
        
        # Obtener los ids de las contratas relacionadas al usuario_rol_contrata_id
        contratas_ids = list(db.usuarios_contratas.find(
            {'usuario_rol_contrata_id': ObjectId(usuario_rol_contrata_id)},
            {'contrata_id': 1}
        ))

        # Obtener las contratas
        contratas = []
        for contratas_id in contratas_ids:
            contrata = db.contratas.find_one({'_id': contratas_id['contrata_id']})
            if contrata:
                if filtrar_contrata:
                    if (filtrar_contrata.lower() not in contrata['nombre_contrata'].lower() and
                        filtrar_contrata.lower() not in contrata['cif_dni'].lower() and
                        filtrar_contrata.lower() not in contrata['domicilio'].lower() and
                        filtrar_contrata.lower() not in contrata['codigo_postal'].lower() and
                        filtrar_contrata.lower() not in contrata['poblacion'].lower() and
                        filtrar_contrata.lower() not in contrata['provincia'].lower() and
                        filtrar_contrata.lower() not in contrata['telefono_contrata'].lower() and
                        filtrar_contrata.lower() not in contrata['email_contrata'].lower()):
                        continue

                contratas.append({
                    'contrata_id': str(contrata['_id']),
                    'nombre_contrata': contrata['nombre_contrata'],
                    'cif_dni': contrata['cif_dni'],
                    'domicilio': contrata['domicilio'],
                    'codigo_postal': contrata['codigo_postal'],
                    'poblacion': contrata['poblacion'],
                    'provincia': contrata['provincia'],
                    'telefono_contrata': contrata['telefono_contrata'],
                    'email_contrata': contrata['email_contrata']
                })

        return render_template('usuarios/usuarios_contratas.html',
                               usuario_rol_contrata_id=usuario_rol_contrata_id,
                               usuario_contrata=usuario,
                               contratas=contratas,
                               filtrar_contrata=filtrar_contrata
                               )
    
    except Exception as e:
        flash(f'Error al cargar la vista de usuarios contratas: {str(e)}', 'danger')
        return redirect(url_for('usuarios.usuarios'))
    
def usuarios_contratas_contrata_vista(usuario_rol_contrata_id, contrata_id):
    '''
    Vista de usuarios de contratas para la contrata seleccionada.
    '''
    try:
        # Obtener nombre de la contrata
        nombre_contrata = db.contratas.find_one({'_id': ObjectId(contrata_id)})['nombre_contrata']
        
        return render_template('usuarios_contratas/contratas/index.html',
                               usuario_rol_contrata_id=usuario_rol_contrata_id,
                               contrata_id=contrata_id,
                               nombre_contrata=nombre_contrata
                               )
    except Exception as e:
        flash(f'Error al cargar la vista de la contrata: {str(e)}', 'danger')
        return redirect(url_for('usuarios_contratas.usuarios_contratas'))
