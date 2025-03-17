class UsuariosTitularesCollection:
    def __init__(self, 
                 usuario_id,
                 gestor_id,
                 alias,
                 fecha_alta, 
                 fecha_modificacion, 
                 fecha_baja, 
                 estado):
        self.usuario_id = usuario_id
        self.gestor_id = gestor_id
        self.alias = alias
        self.fecha_alta = fecha_alta
        self.fecha_modificacion = fecha_modificacion
        self.fecha_baja = fecha_baja
        self.estado = estado 