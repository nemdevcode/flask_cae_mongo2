from flask import render_template

def usuarios_contratas_vista(gestor_id, titular_id, contrata_id):
    print(gestor_id, titular_id, contrata_id)
    return render_template('usuarios_gestores/usuarios_contratas/listar.html', gestor_id=gestor_id, titular_id=titular_id, contrata_id=contrata_id)

def usuarios_contratas_crear_vista(gestor_id, titular_id, contrata_id):
    return render_template('usuarios_gestores/usuarios_contratas/crear.html', gestor_id=gestor_id, titular_id=titular_id, contrata_id=contrata_id)

def usuarios_contratas_actualizar_vista(gestor_id, titular_id, contrata_id, usuario_contrata_id):
    return render_template('usuarios_gestores/usuarios_contratas/actualizar.html', gestor_id=gestor_id, titular_id=titular_id, contrata_id=contrata_id, usuario_contrata_id=usuario_contrata_id)

def usuarios_contratas_eliminar_vista(gestor_id, titular_id, contrata_id, usuario_contrata_id):
    return render_template('usuarios_gestores/usuarios_contratas/eliminar.html')


