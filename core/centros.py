from flask import render_template


def gestores_centros_vista():
    return render_template('gestores.gestores_centros.html')

def gestores_centros_crear_vista():
    return render_template('gestores.gestores_centros_crear.html')

def gestores_centros_actualizar_vista():
    return render_template('gestores.gestores_centros_actualizar.html')

def gestores_centros_eliminar_vista():
    return render_template('gestores.gestores_centros_eliminar.html')