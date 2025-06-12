from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Miembro, Sancion, SolicitudCorreccion
from .serializers import MiembroSerializer, SancionSerializer, SolicitudCorreccionSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado: permite lectura a todos los autenticados,
    pero solo permite escritura a usuarios admin (is_staff).
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class IsSuperUserOnly(permissions.BasePermission):
    """
    Permite acceso solo a superusuarios.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class MiembroViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Miembro:
    - Solo admins pueden crear, actualizar.
    - Nadie puede eliminar (se gestiona con 'activo').
    """
    queryset = Miembro.objects.all()
    serializer_class = MiembroSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_destroy(self, instance):
        """
        Bloquea el borrado. En lugar de eso, los miembros deben ser desactivados.
        """
        raise PermissionDenied("No está permitido eliminar miembros. Solo pueden ser desactivados.")


class SancionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Sanciones:
    - Solo usuarios staff pueden imponer sanciones.
    - Se muestra el nombre del miembro sancionado.
    """
    queryset = Sancion.objects.all()
    serializer_class = SancionSerializer
    permission_classes = [permissions.IsAdminUser]


class SolicitudCorreccionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Solicitudes de Corrección:
    - Los miembros pueden enviar solicitudes (POST).
    - Solo los admins pueden editar el estado o responderlas.
    """
    queryset = SolicitudCorreccion.objects.all()
    serializer_class = SolicitudCorreccionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        user = self.request.user
        if not user.is_staff:
            raise PermissionDenied("Solo los administradores pueden actualizar solicitudes.")
        serializer.save()
