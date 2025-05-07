from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from utils.usuario_utils import obtener_usuario_autenticado
from utils.rol_utils import verificar_rol_contrata
from config import conexion_mongo

db = conexion_mongo()

def titulares_vista(usuario_rol_contrata_id):
    '''
    Vista de usuarios de contratas para ver los titulares asignados a la contrata.
    '''
    

    return render_template('usuarios_contratas/titulares.html',
                           usuario_rol_contrata_id=usuario_rol_contrata_id)
