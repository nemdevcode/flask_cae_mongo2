from flask_mail import Mail

# Instancia global de Mail
mail = Mail()

def init_extensions(app):
    """Inicializa todas las extensiones de Flask"""
    mail.init_app(app) 