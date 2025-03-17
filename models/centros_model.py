class CentrosCollection:
    def __init__(self, 
                 titular_id,
                 nombre_centro,
                 domicilio,
                 codigo_postal,
                 poblacion,
                 provincia,
                 fecha_alta, 
                 fecha_modificacion, 
                 fecha_baja, 
                 estado):
        self.titular_id = titular_id
        self.nombre_centro = nombre_centro
        self.domicilio = domicilio
        self.codigo_postal = codigo_postal
        self.poblacion = poblacion
        self.provincia = provincia
        self.fecha_alta = fecha_alta
        self.fecha_modificacion = fecha_modificacion
        self.fecha_baja = fecha_baja
        self.estado = estado                 

class UsuariosCentrosCollection:
    def __init__(self, 
                 usuario_id,
                 centro_id,
                 alias,
                 fecha_alta, 
                 fecha_modificacion, 
                 fecha_baja, 
                 estado):
        self.usuario_id = usuario_id
        self.centro_id = centro_id
        self.alias = alias
        self.fecha_alta = fecha_alta
        self.fecha_modificacion = fecha_modificacion
        self.fecha_baja = fecha_baja
        self.estado = estado 

