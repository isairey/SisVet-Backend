import pytest
from django.urls import reverse
from rest_framework import status
from usuarios.models import ResetPasswordToken
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
class TestResetPasswordFlow:
    def test_request_creates_token(self, api_client, usuario_cliente, monkeypatch):
        api_client.force_authenticate(user=None)
        url = reverse('reset_password_request')
        # Patch the notification sender to avoid real email
        monkeypatch.setattr('notificaciones.services.enviar_notificacion_generica', lambda evento, context, to_email: None)

        response = api_client.post(url, {'email': usuario_cliente.email}, format='json')
        assert response.status_code == status.HTTP_200_OK
        # Token should exists
        tokens = ResetPasswordToken.objects.filter(usuario=usuario_cliente)
        assert tokens.exists()

    def test_request_nonexistent_email(self, api_client):
        url = reverse('reset_password_request')
        response = api_client.post(url, {'email': 'noexiste@test.com'}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_token_expired(self, api_client, usuario_cliente):
        token = ResetPasswordToken.create_for_user(usuario_cliente, minutes=1)
        # Force expiration
        token.expires_at = timezone.now() - timedelta(minutes=5)
        token.save()

        url = reverse('reset_password_confirm')
        data = {'token': token.token, 'password': 'newpass123', 'password2': 'newpass123'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'token' in response.data

    def test_confirm_success(self, api_client, usuario_cliente, monkeypatch):
        token = ResetPasswordToken.create_for_user(usuario_cliente, minutes=60)
        url = reverse('reset_password_confirm')
        data = {'token': token.token, 'password': 'newpass123', 'password2': 'newpass123'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        # Refresh user from db
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(pk=usuario_cliente.pk)
        assert user.check_password('newpass123')
        token.refresh_from_db()
        assert token.usado is True

    def test_confirm_invalid_token(self, api_client):
        url = reverse('reset_password_confirm')
        data = {'token': 'invalido', 'password': 'x', 'password2': 'x'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_confirm_password_mismatch(self, api_client, usuario_cliente):
        token = ResetPasswordToken.create_for_user(usuario_cliente, minutes=60)
        url = reverse('reset_password_confirm')
        data = {'token': token.token, 'password': 'a', 'password2': 'b'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password2' in response.data

    def test_token_already_used(self, api_client, usuario_cliente):
        token = ResetPasswordToken.create_for_user(usuario_cliente, minutes=60)
        token.usado = True
        token.save()

        url = reverse('reset_password_confirm')
        data = {'token': token.token, 'password': 'newpass', 'password2': 'newpass'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'token' in response.data
