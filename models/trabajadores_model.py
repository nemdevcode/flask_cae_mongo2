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

    def to_dict(self):
        return {
            'contrata_id': self.contrata_id,
            'nombre_trabajador': self.nombre_trabajador,
            'apellidos_trabajador': self.apellidos_trabajador,
            'dni_nie': self.dni_nie,
            'puesto_trabajo': self.puesto_trabajo,
            'categoria_profesional': self.categoria_profesional,
            'fecha_activacion': self.fecha_activacion,
            'fecha_modificacion': self.fecha_modificacion,
            'fecha_inactivacion': self.fecha_inactivacion,
            'estado_trabajador': self.estado_trabajador
        }
    
class TrabajadoresCentrosCollection:
    def __init__(self,
                 trabajador_id,
                 centro_id,
                 estado_trabajador_centro):
        self.trabajador_id = trabajador_id
        self.centro_id = centro_id
        self.estado_trabajador_centro = estado_trabajador_centro
        
    def to_dict(self):
        return {
            'trabajador_id': self.trabajador_id,
            'centro_id': self.centro_id,
            'estado_trabajador_centro': self.estado_trabajador_centro
        }
