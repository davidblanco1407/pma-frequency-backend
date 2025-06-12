from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MiembroViewSet, SancionViewSet, SolicitudCorreccionViewSet

router = DefaultRouter()
router.register(r'miembros', MiembroViewSet, basename='miembro')
router.register(r'sanciones', SancionViewSet, basename='sancion')
router.register(r'solicitudes', SolicitudCorreccionViewSet, basename='solicitud')

urlpatterns = [
    path('', include(router.urls)),
]
