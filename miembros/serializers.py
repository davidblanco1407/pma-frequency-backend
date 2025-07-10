from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Miembro, Sancion, SolicitudCorreccion
from .utils import crear_usuario_para_miembro, enviar_correo_bienvenida


class MiembroSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Miembro. Incluye la creación
    de usuario de Django, el envío de correo de bienvenida y
    devuelve también el rol del usuario (staff y superuser).
    """
    is_staff = serializers.SerializerMethodField()
    is_superuser = serializers.SerializerMethodField()

    class Meta:
        model = Miembro
        fields = [
            'id',
            'nombre_completo',
            'email',
            'pais',
            'telefono',
            'activo',
            'puede_volver',
            'fecha_registro',
            'fecha_desactivacion',
            'desactivado_por',
            'is_staff',
            'is_superuser',
        ]
        read_only_fields = ['fecha_registro', 'fecha_desactivacion', 'desactivado_por']

    def get_is_staff(self, obj):
        try:
            user = User.objects.get(email=obj.email)
            return user.is_staff
        except User.DoesNotExist:
            return False

    def get_is_superuser(self, obj):
        try:
            user = User.objects.get(email=obj.email)
            return user.is_superuser
        except User.DoesNotExist:
            return False

    def create(self, validated_data):
        email = validated_data.get('email')
        nombre = validated_data.get('nombre_completo')

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Ya existe un usuario con este correo.")

        user, password, username = crear_usuario_para_miembro(email, nombre)
        miembro = Miembro.objects.create(**validated_data)
        enviar_correo_bienvenida(nombre, username, email, password)
        return miembro

    def update(self, instance, validated_data):
        user = self.context['request'].user
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save(user=user)
        return instance


class SancionSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Sancion. Asigna automáticamente
    el usuario que impone la sanción.
    """
    miembro_nombre = serializers.CharField(source='miembro.nombre_completo', read_only=True)

    class Meta:
        model = Sancion
        fields = '__all__'
        read_only_fields = ['fecha', 'impuesta_por', 'miembro_nombre']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['impuesta_por'] = user
        return super().create(validated_data)


class SolicitudCorreccionSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo SolicitudCorreccion. Asocia
    automáticamente la solicitud al miembro autenticado.
    """
    miembro_nombre = serializers.CharField(source='miembro.nombre_completo', read_only=True)

    class Meta:
        model = SolicitudCorreccion
        fields = '__all__'
        read_only_fields = ['fecha', 'estado', 'respuesta', 'miembro', 'miembro_nombre']

    def create(self, validated_data):
        user = self.context['request'].user
        try:
            miembro = Miembro.objects.get(email=user.email)
        except Miembro.DoesNotExist:
            raise serializers.ValidationError("No se encontró un perfil de miembro asociado a este usuario.")
        validated_data['miembro'] = miembro
        return super().create(validated_data)

#Serializer para filtros
class MiembroFiltroSerializer(serializers.Serializer):
    nombre = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    telefono = serializers.CharField(required=False)
    activo = serializers.BooleanField(required=False)
    puede_volver = serializers.BooleanField(required=False)
    fecha_desde = serializers.DateField(required=False)
    fecha_hasta = serializers.DateField(required=False)
