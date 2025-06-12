from rest_framework import serializers
from .models import Miembro, Sancion, SolicitudCorreccion


class MiembroSerializer(serializers.ModelSerializer):
    """
    Serializador para Miembro con control de lectura en campos protegidos
    y validación personalizada para control de activación por superusuarios.
    """
    class Meta:
        model = Miembro
        fields = '__all__'
        read_only_fields = ['fecha_registro', 'fecha_desactivacion', 'desactivado_por']

    def update(self, instance, validated_data):
        """
        Sobrescribe el método update para pasar el usuario autenticado
        al método save(), lo que permite aplicar reglas de reactivación.
        """
        user = self.context['request'].user
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save(user=user)
        return instance


class SancionSerializer(serializers.ModelSerializer):
    """
    Serializador para registrar y consultar sanciones aplicadas a miembros.
    Incluye el nombre del miembro para facilitar la lectura desde el frontend.
    """
    miembro_nombre = serializers.CharField(source='miembro.nombre_completo', read_only=True)

    class Meta:
        model = Sancion
        fields = '__all__'
        read_only_fields = ['fecha', 'impuesta_por', 'miembro_nombre']

    def create(self, validated_data):
        """
        Asigna automáticamente el usuario autenticado como quien impone la sanción.
        """
        user = self.context['request'].user
        validated_data['impuesta_por'] = user
        return super().create(validated_data)


class SolicitudCorreccionSerializer(serializers.ModelSerializer):
    """
    Serializador para registrar y consultar solicitudes de corrección.
    El campo miembro se asocia automáticamente según el usuario autenticado.
    """
    miembro_nombre = serializers.CharField(source='miembro.nombre_completo', read_only=True)

    class Meta:
        model = SolicitudCorreccion
        fields = '__all__'
        read_only_fields = ['fecha', 'estado', 'respuesta', 'miembro_nombre']

    def create(self, validated_data):
        """
        Asocia automáticamente la solicitud al Miembro correspondiente
        según el email del usuario autenticado.
        """
        user = self.context['request'].user
        try:
            miembro = Miembro.objects.get(email=user.email)
        except Miembro.DoesNotExist:
            raise serializers.ValidationError("No se encontró un perfil de miembro asociado a este usuario.")
        validated_data['miembro'] = miembro
        return super().create(validated_data)
