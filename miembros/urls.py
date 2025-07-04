from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MiembroViewSet,
    SancionViewSet,
    SolicitudCorreccionViewSet,
    CambiarPasswordView,
    EnviarCorreoResetPasswordView,
    ResetPasswordConfirmView,
    VerMiPerfilView
)

router = DefaultRouter()
router.register(r'miembros', MiembroViewSet, basename='miembro')
router.register(r'sanciones', SancionViewSet, basename='sancion')
router.register(r'solicitudes', SolicitudCorreccionViewSet, basename='solicitud')

urlpatterns = [
    path('', include(router.urls)),
    path('mi-perfil/', VerMiPerfilView.as_view(), name='mi-perfil'),
    path('cambiar-password/', CambiarPasswordView.as_view(), name='cambiar-password'),
    path('recuperar-password/', EnviarCorreoResetPasswordView.as_view(), name='recuperar-password'),
    path('reset-password/<uidb64>/<token>/', ResetPasswordConfirmView.as_view(), name='reset-password'),
]
