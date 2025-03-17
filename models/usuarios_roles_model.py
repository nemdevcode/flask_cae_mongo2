class UsuariosRolesCollection:
    def __init__(self, 
                 usuario_id, 
                 rol_id, 
                 fecha_alta, 
                 fecha_modificacion, 
                 fecha_baja, 
                 estado):
        self.usuario_id = usuario_id
        self.rol_id = rol_id
        self.fecha_alta = fecha_alta
        self.fecha_modificacion = fecha_modificacion
        self.fecha_baja = fecha_baja
        self.estado = estado