from flask import render_template, request, redirect, url_for, session, flash
from config import conexion_mongo

db = conexion_mongo()

def usuarios_titulares_vista(usuario_rol_id, usuario_rol_gestor_id):
    '''
    Vista para mostrar los titulares relacionados con el usuario gestor que los gestiona. 
    Muestra los titulares activos y permite filtrar por la informacion contenida en la variable filtrar_gestor y por estado.
    '''
    return render_template('usuarios_titulares/index.html', 
                               usuario_rol_id=usuario_rol_id,
                               usuario_rol_gestor_id=usuario_rol_gestor_id
                               )

def usuarios_titulares_gestor_vista(usuario_rol_id, usuario_rol_gestor_id, gestor_id):
    '''
    Vista del titular seleccionado relacionados con el usuario titular autenticado.
    '''
    pass