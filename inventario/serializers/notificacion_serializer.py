from rest_framework import serializers
from inventario.models import Notificacion


class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = '__all__'