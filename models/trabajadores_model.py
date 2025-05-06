class TrabajadoresCollection:
    def __init__(self,
                 contrata_id,
                 dni_nif,
                 nombre_trabajador,
                 apellidos_trabajador,
                 puesto_trabajo,
                 fecha_activacion,
                 fecha_modificacion,
                 fecha_inactivacion,
                 estado_trabajador):
        self.contrata_id = contrata_id
        self.dni_nif = dni_nif
        self.nombre_trabajador = nombre_trabajador
        self.apellidos_trabajador = apellidos_trabajador
        self.puesto_trabajo = puesto_trabajo
        self.fecha_activacion = fecha_activacion
        self.fecha_modificacion = fecha_modificacion
        self.fecha_inactivacion = fecha_inactivacion
        self.estado_trabajador = estado_trabajador