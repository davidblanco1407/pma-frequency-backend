"""
URL configuration for core project.
"""

from django.contrib import admin
from django.urls import path, include
from miembros.views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT Auth personalizado (bloquea miembros inactivos)
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Rutas del módulo miembros
    path('api/miembros/', include('miembros.urls')),
]
