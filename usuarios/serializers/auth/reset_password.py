"""
Reset password serializers - Gestión de tokens para restablecimiento de contraseña.
"""
from rest_framework import serializers
from django.utils import timezone
from usuarios.models import ResetPasswordToken
from django.contrib.auth import get_user_model


class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        User = get_user_model()
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('No existe un usuario con ese correo.')
        return value


class ResetPasswordConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(min_length=6)
    password2 = serializers.CharField(min_length=6)

    def validate(self, data):
        token = data.get('token')
        try:
            token_obj = ResetPasswordToken.objects.select_related('usuario').get(token=token)
        except ResetPasswordToken.DoesNotExist:
            raise serializers.ValidationError({'token': 'Token inválido.'})

        if token_obj.usado:
            raise serializers.ValidationError({'token': 'Token ya fue utilizado.'})

        if token_obj.is_expired:
            raise serializers.ValidationError({'token': 'Token expirado.'})

        if data.get('password') != data.get('password2'):
            raise serializers.ValidationError({'password2': 'Las contraseñas no coinciden.'})

        data['token_obj'] = token_obj
        return data
