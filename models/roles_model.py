class RolesCollection:
    def __init__(self, 
                 nombre_rol, 
                 descripcion, 
                 fecha_activacion, 
                 fecha_modificacion, 
                 fecha_inactivacion, 
                 estado_rol):
        self.nombre_rol = nombre_rol
        self.descripcion = descripcion
        self.fecha_activacion = fecha_activacion
        self.fecha_modificacion = fecha_modificacion
        self.fecha_inactivacion = fecha_inactivacion
        self.estado_rol = estado_rol