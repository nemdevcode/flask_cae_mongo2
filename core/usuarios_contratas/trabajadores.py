from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from utils.usuario_utils import obtener_usuario_autenticado
from utils.rol_utils import verificar_rol_contrata
from config import conexion_mongo

db = conexion_mongo()

def trabajadores_vista():
    '''
    Vista de usuarios de contratas para gestionar trabajadores.
    '''
    pass
