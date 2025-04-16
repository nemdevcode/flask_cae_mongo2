from flask import render_template, redirect, url_for, request, session, flash
from bson import ObjectId
from datetime import datetime
from models.centros_model import UsuariosCentrosCollection
from models.centros_model import CentrosCollection
from utils.usuario_rol_utils import obtener_usuario_rol
from config import conexion_mongo

db = conexion_mongo()


def usuarios_centros_vista(gestor_id, titular_id, centro_id):
    

    return render_template('usuarios_gestores/usuarios_centros/listar.html', 
                           gestor_id=gestor_id,
                           titular_id=titular_id,
                           centro_id=centro_id)

def usuarios_centros_crear_vista():
    return render_template('usuarios_gestores/usuarios_centros/crear.html')

def usuarios_centros_actualizar_vista():
    return render_template('usuarios_gestores/usuarios_centros/actualizar.html')

def usuarios_centros_eliminar_vista():
    return render_template('usuarios_gestores/usuarios_centros/eliminar.html')
                             
