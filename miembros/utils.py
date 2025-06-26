# miembros/utils.py

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings


def generar_username_unico(email):
    base_username = email.split('@')[0]
    username = base_username
    i = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{i}"
        i += 1
    return username


def crear_usuario_para_miembro(email, password=None):
    username = generar_username_unico(email)
    password = password or get_random_string(length=10)
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        is_staff=False
    )
    return user, password


def enviar_correo_bienvenida(nombre, email, password):
    asunto = "¡Bienvenido a PMA Frequency 🎧!"
    mensaje = f"""
Hola {nombre},

Has sido registrado como miembro en la comunidad PMA Frequency.

Tus credenciales de acceso:

📧 Usuario: {email}
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
