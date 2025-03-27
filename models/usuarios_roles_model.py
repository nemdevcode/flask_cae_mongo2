class UsuariosRolesCollection:
    def __init__(self,
                 usuario_id,
                 rol_id,
                 fecha_activacion,
                 fecha_modificacion,
                 fecha_inactivacion,
                 estado_usuario_rol):
        self.usuario_id = usuario_id
        self.rol_id = rol_id
        self.fecha_activacion = fecha_activacion
        self.fecha_modificacion = fecha_modificacion
        self.fecha_inactivacion = fecha_inactivacion
        self.estado_usuario_rol = estado_usuario_rol