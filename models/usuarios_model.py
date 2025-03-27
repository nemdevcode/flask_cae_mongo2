class UsuariosCollection:
    def __init__(self,
                 nombre_usuario,
                 email,
                 telefono,
                 password=None,
                 fecha_activacion=None,
                 fecha_modificacion=None,
                 fecha_inactivacion=None,
                 estado_usuario='pendiente',
                 token_verificacion=None,
                 verificado=False):
        self.nombre_usuario = nombre_usuario
        self.email = email
        self.telefono = telefono
        self.password = password
        self.fecha_activacion = fecha_activacion
        self.fecha_modificacion = fecha_modificacion
        self.fecha_inactivacion = fecha_inactivacion
        self.estado_usuario = estado_usuario
        self.token_verificacion = token_verificacion
        self.verificado = verificado
