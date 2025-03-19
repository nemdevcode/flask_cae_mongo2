from flask import render_template, session
from bson.objectid import ObjectId
from models.usuarios_model import UsuariosCollection
from models.roles_model import RolesCollection
from models.usuarios_roles_model import UsuariosRolesCollection

from config import conexion_mongo

db = conexion_mongo()

def gestores_vista():
    gestor_id = session.get('gestor')
    
    try:
        gestor = db.usuarios.find_one({"_id": ObjectId(gestor_id)})
        
        if gestor:
            nombre_gestor = gestor.get('nombre_usuario')
            return render_template('gestores/index.html', nombre_gestor=nombre_gestor)
        else:
            print("No se encontró el gestor")
            
    except Exception as e:
        print(f"Error al buscar gestor: {str(e)}")
    
    return render_template('gestores/index.html')








