
class TitularesCollection:
    def __init__(self, 
                 gestor_id,
                 nombre_titular,
                 cif_dni,
                 domicilio,
                 codigo_postal,
                 poblacion,
                 provincia,
                 telefono_titular,
                 fecha_activacion, 
                 fecha_modificacion, 
                 fecha_inactivacion, 
                 estado_titular):
        self.gestor_id = gestor_id
        self.nombre_titular = nombre_titular
        self.cif_dni = cif_dni
        self.domicilio = domicilio
        self.codigo_postal = codigo_postal
        self.poblacion = poblacion
        self.provincia = provincia
        self.telefono_titular = telefono_titular
        self.fecha_activacion = fecha_activacion
        self.fecha_modificacion = fecha_modificacion
        self.fecha_inactivacion = fecha_inactivacion
        self.estado_titular = estado_titular
        
class UsuariosTitularesCollection:
    def __init__(self, 
                 usuario_rol_titular_id,
                 titular_id,
                 alias_usuario_titular,
                 fecha_activacion, 
                 fecha_modificacion, 
                 fecha_inactivacion, 
                 estado_usuario_titular):
        self.usuario_rol_titular_id = usuario_rol_titular_id
        self.titular_id = titular_id
        self.alias_usuario_titular = alias_usuario_titular
        self.fecha_activacion = fecha_activacion
        self.fecha_modificacion = fecha_modificacion
        self.fecha_inactivacion = fecha_inactivacion
        self.estado_usuario_titular = estado_usuario_titular