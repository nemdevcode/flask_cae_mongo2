from datetime import datetime # Para registrar los datos de acceso en la base de datos
from flask import request, redirect, url_for, render_template, session
from models.usuarios_model import UsuariosCollection
from config import conexion_mongo
from bson.objectid import ObjectId

db = conexion_mongo()

def login_vista():
    
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            usuario = db.usuarios.find_one({'email': email, 'password': password})
            if usuario:
                # Guardamos el ID como string
                session['usuario_id'] = str(usuario['_id'])
                print(f"Usuario encontrado: {usuario}")  # Para debug
                print(f"ID guardado en sesión: {session['usuario_id']}")  # Para debug
                return redirect(url_for('usuarios.usuarios'))
            else:
                return render_template('login.html', mensaje_error="Usuario o contraseña incorrectos")
        except Exception as e:
            print(f"Error en login: {str(e)}")  # Para ver el error en la consola
            return render_template('login.html', mensaje_error=f"Error al procesar el login: {str(e)}")
    return render_template('login.html')
