from rest_framework import viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.conf import settings
from decouple import config
from .models import Miembro, Sancion, SolicitudCorreccion
from .serializers import (
    MiembroSerializer,
    SancionSerializer,
    SolicitudCorreccionSerializer,
MiembroFiltroSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed


# --------------------- PERMISOS PERSONALIZADOS ---------------------

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class IsSuperUserOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


# --------------------- JWT PERSONALIZADO ---------------------

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if not user.is_superuser:
            try:
                miembro = Miembro.objects.get(email=user.email)
                if not miembro.activo:
                    raise AuthenticationFailed("Tu cuenta está desactivada. Contacta con un administrador.")
            except Miembro.DoesNotExist:
                raise AuthenticationFailed("No se encontró un perfil de miembro asociado a este usuario.")

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# --------------------- VIEWS PRINCIPALES ---------------------

class MiembroViewSet(viewsets.ModelViewSet):
    serializer_class = MiembroSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return Miembro.objects.all()
        return Miembro.objects.filter(email=user.email)

    def perform_create(self, serializer):
        user = self.request.user
        if not (user.is_superuser or user.is_staff):
            raise PermissionDenied("Solo el administrador o superusuario puede crear nuevos miembros.")
        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        if instance.activo is False and serializer.validated_data.get("activo", True):
            if not instance.puede_volver and not user.is_superuser:
                raise PermissionDenied("Este miembro no puede ser reactivado. Contacte con soporte.")
        serializer.save(user=user)

    def perform_destroy(self, instance):
        raise PermissionDenied("No está permitido eliminar miembros. Solo pueden ser desactivados.")


class VerMiPerfilView(RetrieveAPIView):
    """
    Devuelve el perfil del miembro autenticado, basado en su correo.
    Solo disponible para usuarios autenticados.
    """
    serializer_class = MiembroSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        miembro = Miembro.objects.filter(email=user.email).first()
        if not miembro:
            raise NotFound("No se encontró tu perfil como miembro.")
        return miembro


class SancionViewSet(viewsets.ModelViewSet):
    queryset = Sancion.objects.all()
    serializer_class = SancionSerializer
    permission_classes = [permissions.IsAdminUser]


class SolicitudCorreccionViewSet(viewsets.ModelViewSet):
    serializer_class = SolicitudCorreccionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return SolicitudCorreccion.objects.all()
        return SolicitudCorreccion.objects.filter(miembro__email=user.email)

    def perform_update(self, serializer):
        user = self.request.user
        if not user.is_staff:
            raise PermissionDenied("Solo los administradores pueden actualizar solicitudes.")
        serializer.save()


# --------------------- NUEVA VISTA: FILTRADO DE MIEMBROS ---------------------

class FiltrarMiembrosView(APIView):
    """
    Vista para filtrar miembros usando parámetros enviados por POST.
    Solo disponible para administradores.
    """

    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = MiembroFiltroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        filtros = serializer.validated_data

        miembros = Miembro.objects.all()

        if filtros.get('nombre'):
            miembros = miembros.filter(nombre_completo__icontains=filtros['nombre'])

        if filtros.get('email'):
            miembros = miembros.filter(email__icontains=filtros['email'])

        if filtros.get('telefono'):
            miembros = miembros.filter(telefono__icontains=filtros['telefono'])

        if 'activo' in filtros:
            miembros = miembros.filter(activo=filtros['activo'])

        if 'puede_volver' in filtros:
            miembros = miembros.filter(puede_volver=filtros['puede_volver'])

        if filtros.get('fecha_desde'):
            miembros = miembros.filter(fecha_registro__date__gte=filtros['fecha_desde'])

        if filtros.get('fecha_hasta'):
            miembros = miembros.filter(fecha_registro__date__lte=filtros['fecha_hasta'])

        resultado = MiembroSerializer(miembros, many=True)
        return Response(resultado.data)


# --------------------- CAMBIO DE CONTRASEÑA ---------------------

class CambiarPasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        actual = request.data.get('password_actual')
        nueva = request.data.get('nueva_password')
        confirmar = request.data.get('confirmar_password')

        if not user.check_password(actual):
            return Response({'error': 'La contraseña actual no es correcta.'}, status=400)

        if nueva != confirmar:
            return Response({'error': 'Las contraseñas nuevas no coinciden.'}, status=400)

        try:
            validate_password(nueva, user=user)
        except DjangoValidationError as e:
            return Response({'error': e.messages}, status=400)

        user.set_password(nueva)
        user.save()
        return Response({'mensaje': 'Contraseña actualizada correctamente.'})


# --------------------- RECUPERACIÓN DE CONTRASEÑA ---------------------

class EnviarCorreoResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Debes proporcionar un correo.'}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'No existe un usuario con ese correo.'}, status=404)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        frontend_url = config('FRONTEND_URL', default='http://localhost:5173')
        reset_link = f"{frontend_url}/reset-password/{uid}/{token}"

        send_mail(
            subject="Restablece tu contraseña - PMA Frequency",
            message=f"Haz clic en el siguiente enlace para restablecer tu contraseña:\n{reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return Response({'mensaje': 'Se ha enviado un enlace de recuperación si el correo es válido.'})


class ResetPasswordConfirmView(APIView):
    def post(self, request, uidb64, token):
        nueva = request.data.get('nueva_password')
        confirmar = request.data.get('confirmar_password')

        if nueva != confirmar:
            return Response({'error': 'Las contraseñas no coinciden.'}, status=400)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({'error': 'Token inválido o usuario no encontrado.'}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'El token no es válido o ha expirado.'}, status=400)

        try:
            validate_password(nueva, user=user)
        except DjangoValidationError as e:
            return Response({'error': e.messages}, status=400)

        user.set_password(nueva)
        user.save()
        return Response({'mensaje': 'Contraseña restablecida correctamente.'})


class EstadisticasView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        activos = Miembro.objects.filter(activo=True).count()
        inactivos = Miembro.objects.filter(activo=False, puede_volver=True).count()
        bloqueados = Miembro.objects.filter(activo=False, puede_volver=False).count()

        return Response({
            "activos": activos,
            "inactivos": inactivos,
            "bloqueados": bloqueados
        })
    