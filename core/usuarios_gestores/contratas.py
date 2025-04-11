from flask import render_template

def contratas_vista():
    return render_template('usuarios_gestores/contratas/listar.html')

def contratas_crear_vista():
    return render_template('usuarios_gestores/contratas/crear.html')

def contratas_actualizar_vista():
    return render_template('usuarios_gestores/contratas/actualizar.html')

def contratas_eliminar_vista():
    return render_template('usuarios_gestores/contratas/eliminar.html')
