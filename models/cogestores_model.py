class UsuariosCogestoresCollection:
    def __init__(self,
                 usuario_rol_id,
                 gestor_id,
                 alias_usuario_cogestor,
                 fecha_activacion,
                 fecha_modificacion,
                 fecha_inactivacion,
                 estado_usuario_cogestor):
        self.usuario_rol_id = usuario_rol_id
        self.gestor_id = gestor_id
        self.alias_usuario_cogestor = alias_usuario_cogestor
        self.fecha_activacion = fecha_activacion
        self.fecha_modificacion = fecha_modificacion
        self.fecha_inactivacion = fecha_inactivacion
        self.estado_usuario_cogestor = estado_usuario_cogestor