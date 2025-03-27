from flask import request, redirect, url_for, render_template, session, flash
# from icecream import ic
from config import conexion_mongo

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
                # ic("Usuario encontrado:", usuario)
                # ic("ID guardado en sesión:", session['usuario_id'])
                return redirect(url_for('usuarios.usuarios'))
            else:
                flash("Usuario o contraseña incorrectos", "danger")
                return render_template('login.html')
        except Exception as e:
            # ic("Error en login:", str(e))
            flash(f"Error al procesar el login: {str(e)}", "danger")
            return render_template('login.html')
    return render_template('login.html')
