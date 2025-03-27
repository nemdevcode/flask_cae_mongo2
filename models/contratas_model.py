class ContratasCollection:
    def __init__(self,
                 nombre_contrata,
                 cif_dni,
                 domicilio,
                 codigo_postal,
                 poblacion,
                 provincia,
                 telefono,
                 fecha_activacion,
                 fecha_modificacion,
                 fecha_inactivacion,
                 estado_contrata):
        self.nombre_contrata = nombre_contrata
        self.cif_dni = cif_dni
        self.domicilio = domicilio
        self.codigo_postal = codigo_postal
        self.poblacion = poblacion
        self.provincia = provincia
        self.telefono = telefono
        self.fecha_activacion = fecha_activacion
        self.fecha_modificacion = fecha_modificacion
        self.fecha_inactivacion = fecha_inactivacion
        self.estado_contrata = estado_contrata

class UsuariosContratasCollection:
    def __init__(self,
                 usuario_rol_id,
                 contrata_id,
                 alias,
                 fecha_activacion,
                 fecha_modificacion,
                 fecha_inactivacion,
                 estado_usuario_contrata):
        self.usuario_rol_id = usuario_rol_id
        self.contrata_id = contrata_id
        self.alias = alias
        self.fecha_activacion = fecha_activacion
        self.fecha_modificacion = fecha_modificacion
        self.fecha_inactivacion = fecha_inactivacion
        self.estado_usuario_contrata = estado_usuario_contrata
