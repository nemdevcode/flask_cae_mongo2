from flask import render_template

def usuarios_contratas_vista():
    return render_template('gestores_usuarios_contratas.html')

def usuarios_contratas_crear_vista():
    return render_template('gestores_usuarios_contratas_crear.html')

def usuarios_contratas_actualizar_vista():
    return render_template('gestores_usuarios_contratas_actualizar.html')

def usuarios_contratas_eliminar_vista():
    return render_template('gestores_usuarios_contratas_eliminar.html')


