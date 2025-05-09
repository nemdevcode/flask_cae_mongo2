class RequerimientosCollection:
    def __init__(self,
                 gestor_id,
                 referencia_requerimiento,
                 nombre_requerimiento,
                 tipo_requerimiento,
                 estado_requerimiento,
                 fecha_activacion,
                 fecha_modificacion,
                 fecha_inactivacion,
                 descripcion_requerimiento=None,
                 notas_requerimiento=None):
        self.gestor_id = gestor_id
        self.referencia_requerimiento = referencia_requerimiento
        self.nombre_requerimiento = nombre_requerimiento
        self.tipo_requerimiento = tipo_requerimiento
        self.estado_requerimiento = estado_requerimiento
        self.fecha_activacion = fecha_activacion
        self.fecha_modificacion = fecha_modificacion
        self.fecha_inactivacion = fecha_inactivacion
        self.descripcion_requerimiento = descripcion_requerimiento
        self.notas_requerimiento = notas_requerimiento

    def to_dict(self):
        return {
            'gestor_id': self.gestor_id,
            'referencia_requerimiento': self.referencia_requerimiento,
            'nombre_requerimiento': self.nombre_requerimiento,
            'tipo_requerimiento': self.tipo_requerimiento,
            'descripcion_requerimiento': self.descripcion_requerimiento,
            'notas_requerimiento': self.notas_requerimiento,
            'estado_requerimiento': self.estado_requerimiento,
            'fecha_activacion': self.fecha_activacion,
            'fecha_modificacion': self.fecha_modificacion,
            'fecha_inactivacion': self.fecha_inactivacion
        }


