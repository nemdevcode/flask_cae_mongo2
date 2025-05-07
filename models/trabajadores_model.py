class TrabajadoresCollection:
    def __init__(self,
                 contrata_id,
                 nombre_trabajador,
                 apellidos_trabajador,
                 dni_nie,
                 puesto_trabajo,
                 categoria_profesional,
                 fecha_activacion,
                 fecha_modificacion,
                 fecha_inactivacion,
                 estado_trabajador):
        self.contrata_id = contrata_id
        self.nombre_trabajador = nombre_trabajador
        self.apellidos_trabajador = apellidos_trabajador
        self.dni_nie = dni_nie
        self.puesto_trabajo = puesto_trabajo
        self.categoria_profesional = categoria_profesional
        self.fecha_activacion = fecha_activacion
        self.fecha_modificacion = fecha_modificacion
        self.fecha_inactivacion = fecha_inactivacion
        self.estado_trabajador = estado_trabajador