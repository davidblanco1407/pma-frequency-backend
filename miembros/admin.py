from django.contrib import admin
from django.utils.html import format_html
from .models import Miembro, Sancion, SolicitudCorreccion


def cambiar_estado_miembro(queryset, activo, puede_volver, user):
    for miembro in queryset:
        miembro.activo = activo
        miembro.puede_volver = puede_volver
        miembro.save(user=user)


@admin.action(description="Reactivar miembros que pueden volver")
def reactivar_miembros(modeladmin, request, queryset):
    cambiar_estado_miembro(queryset.filter(activo=False, puede_volver=True), True, True, request.user)


@admin.action(description="Desactivar miembros (sin impedir regreso)")
def desactivar_miembros_temporal(modeladmin, request, queryset):
    cambiar_estado_miembro(queryset.filter(activo=True), False, True, request.user)


@admin.action(description="Desactivar miembros permanentemente (no pueden volver)")
def desactivar_miembros_permanente(modeladmin, request, queryset):
    cambiar_estado_miembro(queryset.filter(activo=True), False, False, request.user)


@admin.register(Miembro)
class MiembroAdmin(admin.ModelAdmin):
    list_display = (
        'nombre_completo', 'email', 'telefono', 'activo', 'puede_volver',
        'fecha_registro', 'estado_visual'
    )
    list_filter = ('activo', 'puede_volver', 'fecha_registro')
    search_fields = ('nombre_completo', 'email', 'telefono')
    readonly_fields = ('fecha_registro', 'fecha_desactivacion', 'desactivado_por')
    ordering = ('-fecha_registro',)
    actions = [reactivar_miembros, desactivar_miembros_temporal, desactivar_miembros_permanente]
    fieldsets = (
        (None, {
            'fields': ('nombre_completo', 'email', 'telefono', 'activo', 'puede_volver')
        }),
        ('Historial', {
            'fields': ('fecha_registro', 'fecha_desactivacion', 'desactivado_por'),
            'classes': ('collapse',)
        }),
    )

    def estado_visual(self, obj):
        if obj.activo:
            return format_html('<span style="color: green;">Activo</span>')
        elif not obj.puede_volver:
            return format_html('<span style="color: red;">Bloqueado</span>')
        return format_html('<span style="color: orange;">Inactivo</span>')

    estado_visual.short_description = "Estado visual"


@admin.register(Sancion)
class SancionAdmin(admin.ModelAdmin):
    list_display = ('miembro', 'motivo', 'fecha', 'duracion_dias', 'impuesta_por')
    list_filter = ('fecha',)
    search_fields = ('miembro__nombre_completo', 'motivo')
    readonly_fields = ('fecha', 'impuesta_por')
    ordering = ('-fecha',)


@admin.register(SolicitudCorreccion)
class SolicitudCorreccionAdmin(admin.ModelAdmin):
    list_display = ('miembro', 'estado', 'fecha')
    list_filter = ('estado', 'fecha')
    search_fields = ('miembro__nombre_completo', 'descripcion')
    readonly_fields = ('fecha',)
    ordering = ('-fecha',)
