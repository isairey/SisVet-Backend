"""
Reset Password Token model inside auth package.
This is a copy of the existing `usuarios/models/reset_password_token.py` moved to
`usuarios/models/auth/` to centralize auth-related models.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import secrets
from common.models import BaseModel


class ResetPasswordToken(BaseModel):
    """
    Modelo para gestionar tokens de restablecimiento de contraseña.
    """

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reset_tokens'
    )
    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    usado = models.BooleanField(default=False)

    class Meta:
        db_table = 'reset_password_tokens'
        verbose_name = 'Reset Password Token'
        verbose_name_plural = 'Reset Password Tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token', 'usado']),
            models.Index(fields=['usuario', 'usado']),
        ]

    def __str__(self):
        return f"ResetToken({self.usuario.username}, used={self.usado})"

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(48)

    @classmethod
    def create_for_user(cls, usuario, minutes: int = 60) -> 'ResetPasswordToken':
        token = cls.generate_token()
        expires = timezone.now() + timedelta(minutes=minutes)
        return cls.objects.create(usuario=usuario, token=token, expires_at=expires)

    def mark_as_used(self) -> None:
        self.usado = True
        self.save()
