from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generar_token_verificacion(email):
    """
    Genera un token seguro para la verificación de email
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def verificar_token(token, expiration=3600):
    """
    Verifica un token de verificación
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
        return email
    except:
        return False 