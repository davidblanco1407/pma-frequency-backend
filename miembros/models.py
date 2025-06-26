from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField


class Miembro(models.Model):
    """
    Modelo que representa a un miembro registrado en la comunidad PMA Frequency.
    """

    nombre_completo = models.CharField(
        max_length=100,
        verbose_name="Nombre completo",
        help_text="Nombre completo del miembro. Máximo 100 caracteres."
    )

    email = models.EmailField(
        unique=True,
        verbose_name="Correo electrónico",
        help_text="Correo único del miembro. Se usará como identificador de contacto."
    )

    telefono = PhoneNumberField(
        region='CO',
        verbose_name="Número de teléfono",
        help_text="Número válido en formato colombiano o internacional. Requiere código de país."
    )

    activo = models.BooleanField(default=True)

    puede_volver = models.BooleanField(
        default=True,
        verbose_name="¿Puede volver?",
        help_text="Indica si el miembro puede ser reactivado en el futuro."
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_desactivacion = models.DateTimeField(null=True, blank=True)

    desactivado_por = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        if self.activo:
            # Validación: si no puede volver, solo el superusuario puede reactivarlo
            if self.puede_volver is False:
                if user is None or not user.is_superuser:
                    raise ValidationError("Este miembro no puede ser reactivado. Solo un superusuario puede hacerlo.")
            self.fecha_desactivacion = None
            self.desactivado_por = None
        else:
            # Desactivación
            if self.fecha_desactivacion is None:
                self.fecha_desactivacion = timezone.now()
            if user and not self.desactivado_por:
                self.desactivado_por = user

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre_completo

    class Meta:
        verbose_name = "Miembro"
        verbose_name_plural = "Miembros"
        ordering = ['nombre_completo']


class Sancion(models.Model):
    """
    Representa una sanción impuesta a un miembro de la comunidad PMA Frequency.
    Cada sanción está asociada a un miembro específico.
    """

    miembro = models.ForeignKey(
        Miembro,
        on_delete=models.CASCADE,
        related_name='sanciones',
        verbose_name="Miembro sancionado",
        help_text="Miembro al que se le aplica esta sanción."
    )

    motivo = models.TextField(
        verbose_name="Motivo de la sanción",
        help_text="Descripción detallada del motivo de la sanción."
    )

    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de sanción",
        help_text="Fecha y hora en la que se registró la sanción."
    )

    duracion_dias = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Duración (en días)",
        help_text="Duración de la sanción en días (opcional)."
    )

    impuesta_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Sanción impuesta por",
        help_text="Usuario que registró o impuso la sanción."
    )

    def __str__(self):
        return f"Sanción a {self.miembro.nombre_completo} el {self.fecha.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Sanción"
        verbose_name_plural = "Sanciones"
        ordering = ['-fecha']


class EstadoSolicitud(models.TextChoices):
    PENDIENTE = 'pendiente', 'Pendiente'
    APROBADA = 'aprobada', 'Aprobada'
    RECHAZADA = 'rechazada', 'Rechazada'


class SolicitudCorreccion(models.Model):
    """
    Representa una solicitud de corrección enviada por un miembro.
    Puede referirse a sanciones, datos personales u otros elementos del sistema.
    """

    miembro = models.ForeignKey(
        Miembro,
        on_delete=models.CASCADE,
        related_name='solicitudes',
        verbose_name="Miembro solicitante",
        help_text="Miembro que envía la solicitud de corrección."
    )

    descripcion = models.TextField(
        verbose_name="Descripción del problema",
        help_text="Detalle del error o situación que el miembro desea corregir."
    )

    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de solicitud",
        help_text="Fecha y hora en que se envió la solicitud."
    )

    estado = models.CharField(
        max_length=10,
        choices=EstadoSolicitud.choices,
        default=EstadoSolicitud.PENDIENTE,
        verbose_name="Estado",
        help_text="Estado actual de la solicitud."
    )

    respuesta = models.TextField(
        null=True,
        blank=True,
        verbose_name="Respuesta del administrador",
        help_text="Respuesta proporcionada por el administrador (opcional)."
    )

    def __str__(self):
        return f"Solicitud de {self.miembro.nombre_completo} ({self.estado})"

    class Meta:
        verbose_name = "Solicitud de corrección"
        verbose_name_plural = "Solicitudes de corrección"
        ordering = ['-fecha']
