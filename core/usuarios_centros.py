from flask import render_template


def gestores_usuarios_centros_vista():
    return render_template('gestores_usuarios_centros.html')

def gestores_usuarios_centros_crear_vista():
    return render_template('gestores_usuarios_centros_crear.html')

def gestores_usuarios_centros_actualizar_vista():
    return render_template('gestores_usuarios_centros_actualizar.html')

def gestores_usuarios_centros_eliminar_vista():
    return render_template('gestores_usuarios_centros_eliminar.html')