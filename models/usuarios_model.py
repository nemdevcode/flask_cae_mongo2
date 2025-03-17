class UsuariosCollection:
    def __init__(self, 
                 nombre_usuario, 
                 cif_dni, 
                 domicilio, 
                 codigo_postal, 
                 poblacion, 
                 provincia, 
                 telefono, 
                 email, 
                 password, 
                 fecha_alta, 
                 fecha_modificacion, 
                 fecha_baja, 
                 estado):
        self.nombre_usuario = nombre_usuario
        self.cif_dni = cif_dni
        self.domicilio = domicilio
        self.codigo_postal = codigo_postal
        self.poblacion = poblacion
        self.provincia = provincia
        self.telefono = telefono
        self.email = email
        self.password = password
        self.fecha_alta = fecha_alta
        self.fecha_modificacion = fecha_modificacion
        self.fecha_baja = fecha_baja
        self.estado = estado 