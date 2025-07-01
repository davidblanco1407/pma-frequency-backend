from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings


def generar_username_unico(email):
    """
    Genera un nombre de usuario único basado en el email.
    Si ya existe, le añade un número incremental al final.
    """
    base_username = email.split('@')[0]
    username = base_username
    i = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{i}"
        i += 1
    return username


def crear_usuario_para_miembro(email, nombre_completo, password=None):
    """
    Crea un usuario de Django para un nuevo miembro.

    Args:
        email (str): Correo electrónico del miembro.
        nombre_completo (str): Nombre completo del miembro.
        password (str, optional): Contraseña. Si no se proporciona, se genera una aleatoria.

    Returns:
        tuple: (usuario creado, contraseña, username)
    """
    username = generar_username_unico(email)
    password = password or get_random_string(length=10)
    partes_nombre = nombre_completo.strip().split()
    first_name = partes_nombre[0] if partes_nombre else ''
    last_name = ' '.join(partes_nombre[1:]) if len(partes_nombre) > 1 else ''

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_staff=False
    )
    return user, password, username


def enviar_correo_bienvenida(nombre, username, email, password):
    """
    Envía un correo de bienvenida al nuevo miembro con sus credenciales de acceso.

    Args:
        nombre (str): Nombre del miembro.
        username (str): Nombre de usuario asignado.
        email (str): Correo electrónico del miembro.
        password (str): Contraseña temporal.
    """
    asunto = "¡Bienvenido a PMA Frequency 🎧!"
    mensaje = f"""
Hola {nombre},

Has sido registrado como miembro en la comunidad PMA Frequency.

Tus credenciales de acceso:

👤 Usuario: {username}
🔑 Contraseña temporal: {password}

Por favor, inicia sesión y cambia tu contraseña cuanto antes.

— El equipo de PMA Frequency
"""
    send_mail(
        subject=asunto,
        message=mensaje,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False
    )
