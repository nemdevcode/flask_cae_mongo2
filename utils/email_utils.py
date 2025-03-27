from flask_mail import Message
from flask import current_app
from extensions import mail
# from icecream import ic
from dotenv import load_dotenv
import os

def enviar_email(destinatario, asunto, cuerpo):
    """
    Envía un correo electrónico usando Flask-Mail.
    
    Args:
        destinatario (str): Dirección de correo del destinatario
        asunto (str): Asunto del correo
        cuerpo (str): Contenido del correo (puede ser HTML)
    
    Returns:
        bool: True si el correo se envió correctamente, False en caso contrario
    """
    try:
        # Verificar la contraseña directamente
        # ic("Verificando contraseña:")
        # password = current_app.config['MAIL_PASSWORD']
        # ic("Contraseña actual:", password)  # Mostrar la contraseña actual para debugging
        
        # ic("Configuración de correo en Flask:")
        # ic(current_app.config['MAIL_SERVER'])
        # ic(current_app.config['MAIL_PORT'])
        # ic(current_app.config['MAIL_USE_TLS'])
        # ic(current_app.config['MAIL_USE_SSL'])
        # ic("Usuario:", current_app.config['MAIL_USERNAME'])
        
        # ic("Remitente:", current_app.config['MAIL_USERNAME'])
        
        mensaje = Message(
            subject=asunto,
            recipients=[destinatario],
            html=cuerpo,
            sender=current_app.config['MAIL_USERNAME']
        )
        
        # ic("Intentando enviar correo...")
        mail.send(mensaje)
        # ic("Correo enviado exitosamente")
        return True
    except Exception as e:
        # ic("Error al enviar el correo:", str(e))
        # ic("Detalles completos del error:", e)
        return False 