from django.db import models
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField


class Miembro(models.Model):
    """
    Modelo que representa a un miembro registrado en la comunidad PMA Frequency.
    Incluye datos personales, estado y control de reactivación en caso de inactividad.
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

    activo = models.BooleanField(
        default=True,
        verbose_name="¿Está activo?",
        help_text="Define si el miembro está actualmente activo en la comunidad."
    )

    puede_volver = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="¿Puede volver?",
        help_text="Solo aplicable si el miembro ha sido desactivado. Indica si puede reingresar."
    )

    fecha_registro = models.DateField(
        auto_now_add=True,
        verbose_name="Fecha de registro",
        help_text="Fecha automática en la que se registró el miembro en el sistema."
    )

    def clean(self):
        """
        Valida que si el miembro está inactivo, se especifique si puede volver o no.
        """
        if not self.activo and self.puede_volver is None:
            raise ValidationError({
                'puede_volver': "Debes indicar si el miembro puede volver cuando está inactivo."
            })

    def __str__(self):
        """
        Representación legible del objeto.
        """
        return self.nombre_completo

    class Meta:
        verbose_name = "Miembro"
        verbose_name_plural = "Miembros"
        ordering = ['nombre_completo']
