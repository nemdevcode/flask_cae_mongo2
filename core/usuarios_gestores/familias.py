from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from datetime import datetime
from config import conexion_mongo
from models.familias_model import FamiliasCollection

db = conexion_mongo()

def familias_vista(gestor_id, titular_id):
    return render_template('usuarios_gestores/familias/listar.html', 
                           gestor_id=gestor_id, 
                           titular_id=titular_id)

def familias_crear_vista(gestor_id, titular_id):
    return render_template('usuarios_gestores/familias/crear.html', 
                           gestor_id=gestor_id, 
                           titular_id=titular_id)

def familias_actualizar_vista(gestor_id, titular_id, familia_id):
    return render_template('usuarios_gestores/familias/actualizar.html', 
                           gestor_id=gestor_id, 
                           titular_id=titular_id, 
                           familia_id=familia_id)

def familias_eliminar_vista(gestor_id, titular_id, familia_id):
    return render_template('usuarios_gestores/familias/eliminar.html',
                           gestor_id=gestor_id, 
                           titular_id=titular_id, 
                           familia_id=familia_id)
