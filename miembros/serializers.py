from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Miembro, Sancion, SolicitudCorreccion
from .utils import crear_usuario_para_miembro, enviar_correo_bienvenida


class MiembroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Miembro
        fields = '__all__'
        read_only_fields = ['fecha_registro', 'fecha_desactivacion', 'desactivado_por']

    def create(self, validated_data):
        email = validated_data.get('email')
        nombre = validated_data.get('nombre_completo')

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Ya existe un usuario con este correo.")

        user, password = crear_usuario_para_miembro(email)
        miembro = Miembro.objects.create(**validated_data)
        enviar_correo_bienvenida(nombre, email, password)
        return miembro

    def update(self, instance, validated_data):
        user = self.context['request'].user
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save(user=user)
        return instance


class SancionSerializer(serializers.ModelSerializer):
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
    miembro_nombre = serializers.CharField(source='miembro.nombre_completo', read_only=True)

    class Meta:
        model = SolicitudCorreccion
        fields = '__all__'
        read_only_fields = ['fecha', 'estado', 'respuesta', 'miembro_nombre']

    def create(self, validated_data):
        user = self.context['request'].user
        try:
            miembro = Miembro.objects.get(email=user.email)
        except Miembro.DoesNotExist:
            raise serializers.ValidationError("No se encontró un perfil de miembro asociado a este usuario.")
        validated_data['miembro'] = miembro
        return super().create(validated_data)
