from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from datetime import datetime
from config import conexion_mongo

db = conexion_mongo()

def centros_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    return render_template('usuarios_cogestores/centros/listar.html', 
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                           usuario_rol_gestor_id=usuario_rol_gestor_id, 
                           gestor_id=gestor_id, 
                           titular_id=titular_id)

def centros_crear_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    return render_template('usuarios_cogestores/centros/crear.html', 
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                           usuario_rol_gestor_id=usuario_rol_gestor_id, 
                           gestor_id=gestor_id, 
                           titular_id=titular_id)

def centros_actualizar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id):
    return render_template('usuarios_cogestores/centros/actualizar.html', 
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                           usuario_rol_gestor_id=usuario_rol_gestor_id, 
                           gestor_id=gestor_id, 
                           titular_id=titular_id, 
                           centro_id=centro_id)

def centros_eliminar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id):
    return render_template('usuarios_cogestores/centros/eliminar.html', 
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                           usuario_rol_gestor_id=usuario_rol_gestor_id, 
                           gestor_id=gestor_id, 
                           titular_id=titular_id, 
                           centro_id=centro_id)

def centros_centro_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id, centro_id):
    return render_template('usuarios_cogestores/centros/index.html', 
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id, 
                           usuario_rol_gestor_id=usuario_rol_gestor_id, 
                           gestor_id=gestor_id, 
                           titular_id=titular_id, 
                           centro_id=centro_id)


