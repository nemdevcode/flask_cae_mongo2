from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from datetime import datetime
from utils.usuario_utils import obtener_usuario_autenticado
from utils.rol_utils import obtener_rol, verificar_rol_cogestor
from utils.usuario_rol_utils import obtener_usuario_rol
from models.gestores_model import GestoresCollection
from config import conexion_mongo

db = conexion_mongo()

def titulares_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id):
    return render_template('usuarios_cogestores/titulares/listar.html',
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                           usuario_rol_gestor_id=usuario_rol_gestor_id,
                           gestor_id=gestor_id
                           )

def titulares_crear_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id):
    return render_template('usuarios_cogestores/titulares/crear.html',
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                           usuario_rol_gestor_id=usuario_rol_gestor_id,
                           gestor_id=gestor_id
                           )

def titulares_actualizar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    return render_template('usuarios_cogestores/titulares/actualizar.html',
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                           usuario_rol_gestor_id=usuario_rol_gestor_id,
                           gestor_id=gestor_id,
                           titular_id=titular_id
                           )

def titulares_eliminar_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    return render_template('usuarios_cogestores/titulares/eliminar.html',
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                           usuario_rol_gestor_id=usuario_rol_gestor_id,
                           gestor_id=gestor_id,
                           titular_id=titular_id
                           )

def titulares_titular_vista(usuario_rol_cogestor_id, usuario_rol_gestor_id, gestor_id, titular_id):
    return render_template('usuarios_cogestores/titulares/index.html',
                           usuario_rol_cogestor_id=usuario_rol_cogestor_id,
                           usuario_rol_gestor_id=usuario_rol_gestor_id,
                           gestor_id=gestor_id,
                           titular_id=titular_id
                           )

