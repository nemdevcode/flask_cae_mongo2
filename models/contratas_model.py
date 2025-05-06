class ContratasCollection:
    def __init__(self,
                 titular_id,
                 nombre_contrata,
                 cif_dni,
                 domicilio,
                 codigo_postal,
                 poblacion,
                 provincia,
                 telefono_contrata,
                 email_contrata,
                 fecha_activacion,
                 fecha_modificacion,
                 fecha_inactivacion,
                 estado_contrata):
        self.titular_id = titular_id
        self.nombre_contrata = nombre_contrata
        self.cif_dni = cif_dni
        self.domicilio = domicilio
        self.codigo_postal = codigo_postal
        self.poblacion = poblacion
        self.provincia = provincia
        self.telefono_contrata = telefono_contrata
        self.email_contrata = email_contrata
        self.fecha_activacion = fecha_activacion
        self.fecha_modificacion = fecha_modificacion
        self.fecha_inactivacion = fecha_inactivacion
        self.estado_contrata = estado_contrata

class UsuariosContratasCollection:
    def __init__(self,
                 usuario_rol_contrata_id,
                 contrata_id,
                 alias_usuario_contrata,
                 fecha_activacion,
                 fecha_modificacion,
                 fecha_inactivacion,
                 estado_usuario_contrata):
        self.usuario_rol_contrata_id = usuario_rol_contrata_id
        self.contrata_id = contrata_id
        self.alias_usuario_contrata = alias_usuario_contrata
        self.fecha_activacion = fecha_activacion
        self.fecha_modificacion = fecha_modificacion
        self.fecha_inactivacion = fecha_inactivacion
        self.estado_usuario_contrata = estado_usuario_contrata
