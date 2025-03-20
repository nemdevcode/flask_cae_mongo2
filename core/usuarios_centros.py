from flask import render_template


def gestores_usuarios_centros_vista():
    return render_template('gestores/usuarios_centros/listar.html')

def gestores_usuarios_centros_crear_vista():
    return render_template('gestores/usuarios_centros/crear.html')

def gestores_usuarios_centros_actualizar_vista():
    return render_template('gestores/usuarios_centros/actualizar.html')

def gestores_usuarios_centros_eliminar_vista():
    return render_template('gestores/usuarios_centros/eliminar.html')