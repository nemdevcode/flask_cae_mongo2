from flask import render_template


def gestores_usuarios_titulares_vista():
    return render_template('gestores_usuarios_titulares.html')

def gestores_usuarios_titulares_crear_vista():
    return render_template('gestores_usuarios_titulares_crear.html')

def gestores_usuarios_titulares_actualizar_vista():
    return render_template('gestores_usuarios_titulares_actualizar.html')

def gestores_usuarios_titulares_eliminar_vista():
    return render_template('gestores_usuarios_titulares_eliminar.html')

def usuarios_titulares_vista():
    return render_template('usuarios_titulares.html')

def usuarios_titulares_gestor_vista():
    return render_template('usuarios_titulares_gestor.html')