class CentrosCollection:
    def __init__(self, 
                 titular_id,
                 nombre_centro,
                 domicilio,
                 codigo_postal,
                 poblacion,
                 provincia,
                 telefono,
                 fecha_activacion,
                 fecha_modificacion,
                 fecha_inactivacion,
                 estado_centro):
        self.titular_id = titular_id
        self.nombre_centro = nombre_centro
        self.domicilio = domicilio
        self.codigo_postal = codigo_postal
        self.poblacion = poblacion
        self.provincia = provincia
        self.telefono = telefono
        self.fecha_activacion = fecha_activacion
        self.fecha_modificacion = fecha_modificacion
        self.fecha_inactivacion = fecha_inactivacion
        self.estado_centro = estado_centro

class UsuariosCentrosCollection:
    def __init__(self,
                 usuario_rol_id,
                 centro_id,
                 alias,
                 fecha_activacion,
                 fecha_modificacion,
                 fecha_inactivacion,
                 estado_usuario_centro):
        self.usuario_rol_id = usuario_rol_id
        self.centro_id = centro_id
        self.alias = alias
        self.fecha_activacion = fecha_activacion
        self.fecha_modificacion = fecha_modificacion
        self.fecha_inactivacion = fecha_inactivacion
        self.estado_usuario_centro = estado_usuario_centro

