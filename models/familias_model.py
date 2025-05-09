class FamiliasCollection:
    def __init__(self,
                 titular_id,
                 nombre_familia,
                 tipo_familia,
                 fecha_creacion,
                 fecha_modificacion,
                 fecha_inactivacion,
                 descripcion_familia=None,
                 notas_familia=None):
        self.titular_id = titular_id
        self.nombre_familia = nombre_familia
        self.tipo_familia = tipo_familia
        self.fecha_creacion = fecha_creacion
        self.fecha_modificacion = fecha_modificacion
        self.fecha_inactivacion = fecha_inactivacion
        self.descripcion_familia = descripcion_familia
        self.notas_familia = notas_familia

    def to_dict(self):
        return {
            'titular_id': self.titular_id,
            'nombre_familia': self.nombre_familia,
            'tipo_familia': self.tipo_familia,
            'fecha_creacion': self.fecha_creacion,
            'fecha_modificacion': self.fecha_modificacion,
            'fecha_inactivacion': self.fecha_inactivacion,
            'descripcion_familia': self.descripcion_familia,
            'notas_familia': self.notas_familia
        }
