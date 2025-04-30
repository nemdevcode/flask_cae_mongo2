class GestoresCollection:
    def __init__(self,
                 usuario_rol_gestor_id,
                 nombre_gestor,
                 cif_dni,
                 domicilio,
                 codigo_postal,
                 poblacion,
                 provincia,
                 telefono_gestor,
                 fecha_activacion,
                 fecha_modificacion,
                 fecha_inactivacion,
                 estado_gestor):
        self.usuario_rol_gestor_id = usuario_rol_gestor_id
        self.nombre_gestor = nombre_gestor
        self.cif_dni = cif_dni
        self.domicilio = domicilio
        self.codigo_postal = codigo_postal
        self.poblacion = poblacion
        self.provincia = provincia
        self.telefono_gestor = telefono_gestor
        self.fecha_activacion = fecha_activacion
        self.fecha_modificacion = fecha_modificacion
        self.fecha_inactivacion = fecha_inactivacion
        self.estado_gestor = estado_gestor

# class UsuariosGestoresCollection:
#     def __init__(self,
#                  usuario_rol_id,
#                  gestor_id,
#                  fecha_activacion,
#                  fecha_modificacion,
#                  fecha_inactivacion,
#                  estado_usuario_gestor):
#         self.usuario_rol_id = usuario_rol_id
#         self.gestor_id = gestor_id
#         self.fecha_activacion = fecha_activacion
#         self.fecha_modificacion = fecha_modificacion
#         self.fecha_inactivacion = fecha_inactivacion
#         self.estado_usuario_gestor = estado_usuario_gestor

