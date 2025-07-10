from django.contrib import admin
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from .models import Miembro, Sancion, SolicitudCorreccion
from .utils import crear_usuario_para_miembro, enviar_correo_bienvenida


def cambiar_estado_miembro(queryset, activo, puede_volver, user):
    """
    Cambia el estado de un conjunto de miembros de forma segura.

    - Si activo=True, reactiva los miembros.
    - Si activo=False, los desactiva.
    """
    for miembro in queryset:
        miembro.activo = activo
        miembro.puede_volver = puede_volver
        miembro.save(user=user)


@admin.action(description="Reactivar miembros que pueden volver")
def reactivar_miembros(modeladmin, request, queryset):
    """
    Acción de admin para reactivar solo miembros que tienen 'puede_volver=True'.
    """
    cambiar_estado_miembro(queryset.filter(activo=False, puede_volver=True), True, True, request.user)


@admin.action(description="Desactivar miembros (sin impedir regreso)")
def desactivar_miembros_temporal(modeladmin, request, queryset):
    """
    Acción de admin para desactivar miembros temporalmente
    (mantiene 'puede_volver=True').
    """
    cambiar_estado_miembro(queryset.filter(activo=True), False, True, request.user)


@admin.action(description="Desactivar miembros permanentemente (no pueden volver)")
def desactivar_miembros_permanente(modeladmin, request, queryset):
    """
    Acción de admin para desactivar miembros permanentemente
    (pone 'puede_volver=False').
    """
    cambiar_estado_miembro(queryset.filter(activo=True), False, False, request.user)


@admin.register(Miembro)
class MiembroAdmin(admin.ModelAdmin):
    """
    Admin para gestionar Miembros en Django Admin.
    Incluye acciones personalizadas y visualización clara de estado.
    """
    list_display = (
        'nombre_completo', 'email', 'pais', 'telefono', 'activo', 'puede_volver',
        'fecha_registro', 'estado_visual'
    )
    list_filter = ('activo', 'puede_volver', 'fecha_registro')
    search_fields = ('nombre_completo', 'email','pais', 'telefono')
    readonly_fields = ('fecha_registro', 'fecha_desactivacion', 'desactivado_por')
    ordering = ('-fecha_registro',)
    actions = [reactivar_miembros, desactivar_miembros_temporal, desactivar_miembros_permanente]
    fieldsets = (
        (None, {
            'fields': ('nombre_completo', 'email', 'pais', 'telefono', 'activo', 'puede_volver')
        }),
        ('Historial', {
            'fields': ('fecha_registro', 'fecha_desactivacion', 'desactivado_por'),
            'classes': ('collapse',)
        }),
    )

    def estado_visual(self, obj):
        """
        Devuelve un indicador visual del estado del miembro en la lista de admin.
        """
        if obj.activo:
            return format_html('<span style="color: green;">Activo</span>')
        elif not obj.puede_volver:
            return format_html('<span style="color: red;">Bloqueado</span>')
        return format_html('<span style="color: orange;">Inactivo</span>')

    estado_visual.short_description = "Estado visual"

    def save_model(self, request, obj, form, change):
        """
        Controla la creación de un nuevo miembro desde el admin.
        Genera un usuario de Django y envía correo de bienvenida solo al crear.
        """
        if not change:
            if not obj.email:
                raise ValidationError("Debes proporcionar un correo electrónico válido.")
            user, password, username = crear_usuario_para_miembro(obj.email, obj.nombre_completo)
            enviar_correo_bienvenida(obj.nombre_completo, username, obj.email, password)
        super().save_model(request, obj, form, change)


@admin.register(Sancion)
class SancionAdmin(admin.ModelAdmin):
    """
    Admin para Sanciones.
    """
    list_display = ('miembro', 'motivo', 'fecha', 'duracion_dias', 'impuesta_por')
    list_filter = ('fecha',)
    search_fields = ('miembro__nombre_completo', 'motivo')
    readonly_fields = ('fecha', 'impuesta_por')
    ordering = ('-fecha',)


@admin.register(SolicitudCorreccion)
class SolicitudCorreccionAdmin(admin.ModelAdmin):
    """
    Admin para Solicitudes de Corrección.
    """
    list_display = ('miembro', 'estado', 'fecha')
    list_filter = ('estado', 'fecha')
    search_fields = ('miembro__nombre_completo', 'descripcion')
    readonly_fields = ('fecha',)
    ordering = ('-fecha',)
