from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import Miembro, Sancion, SolicitudCorreccion


class MiembroSerializer(serializers.ModelSerializer):
    """
    Serializador para Miembro con creación automática de usuario y envío de contraseña por correo.
    También incluye validaciones para activación por superusuario y campos de solo lectura.
    """
    class Meta:
        model = Miembro
        fields = '__all__'
        read_only_fields = ['fecha_registro', 'fecha_desactivacion', 'desactivado_por']

    def create(self, validated_data):
        email = validated_data.get('email')
        nombre = validated_data.get('nombre_completo')

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Ya existe un usuario con este correo.")

        # Generar username y contraseña aleatoria
        username = email.split('@')[0]
        password = get_random_string(length=10)

        # Crear el usuario
        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=False  # el miembro NO es admin
        )

        # Crear el miembro
        miembro = Miembro.objects.create(**validated_data)

        # Enviar correo con contraseña
        send_mail(
            subject="¡Bienvenido a PMA Frequency 🎧!",
            message=f"""
Hola {nombre},

Has sido registrado como miembro en la comunidad PMA Frequency.

Tus credenciales de acceso:

📧 Usuario: {email}
🔑 Contraseña temporal: {password}

Por favor, inicia sesión y cambia tu contraseña cuanto antes.

— El equipo de PMA Frequency
""",
            from_email=None,  # usa DEFAULT_FROM_EMAIL
            recipient_list=[email],
            fail_silently=False
        )

        return miembro

    def update(self, instance, validated_data):
        """
        Actualización con paso del usuario autenticado para control de reactivación.
        """
        user = self.context['request'].user
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save(user=user)
        return instance


class SancionSerializer(serializers.ModelSerializer):
    """
    Serializador para registrar y consultar sanciones aplicadas a miembros.
    Incluye el nombre del miembro para facilitar la lectura desde el frontend.
    """
    miembro_nombre = serializers.CharField(source='miembro.nombre_completo', read_only=True)

    class Meta:
        model = Sancion
        fields = '__all__'
        read_only_fields = ['fecha', 'impuesta_por', 'miembro_nombre']

    def create(self, validated_data):
        """
        Asigna automáticamente el usuario autenticado como quien impone la sanción.
        """
        user = self.context['request'].user
        validated_data['impuesta_por'] = user
        return super().create(validated_data)


class SolicitudCorreccionSerializer(serializers.ModelSerializer):
    """
    Serializador para registrar y consultar solicitudes de corrección.
    El campo miembro se asocia automáticamente según el usuario autenticado.
    """
    miembro_nombre = serializers.CharField(source='miembro.nombre_completo', read_only=True)

    class Meta:
        model = SolicitudCorreccion
        fields = '__all__'
        read_only_fields = ['fecha', 'estado', 'respuesta', 'miembro_nombre']

    def create(self, validated_data):
        """
        Asocia automáticamente la solicitud al Miembro correspondiente
        según el email del usuario autenticado.
        """
        user = self.context['request'].user
        try:
            miembro = Miembro.objects.get(email=user.email)
        except Miembro.DoesNotExist:
            raise serializers.ValidationError("No se encontró un perfil de miembro asociado a este usuario.")
        validated_data['miembro'] = miembro
        return super().create(validated_data)
