from flask import render_template

def gestores_contratas_vista():
    return render_template('usuarios_gestores/contratas/listar.html')

def gestores_contratas_crear_vista():
    return render_template('usuarios_gestores/contratas/crear.html')

def gestores_contratas_actualizar_vista():
    return render_template('usuarios_gestores/contratas/actualizar.html')

def gestores_contratas_eliminar_vista():
    return render_template('usuarios_gestores/contratas/eliminar.html')
