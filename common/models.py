import uuid
from django.db import models
from django.utils import timezone

# Jeronimo Rodriguez 10/28/2025 
class BaseModel(models.Model):
    """
    Clase abstracta base para todos los modelos del sistema.
    Proporciona campos comunes de auditoría y un ID UUID único.
    """
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField('Fecha de creación', default=timezone.now)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)
    deleted_at = models.DateTimeField('Fecha de eliminación', null=True, blank=True)

    class Meta:
        abstract = True  # No crea tabla propia
        ordering = ['-created_at']

    def soft_delete(self):
        """Marca el registro como eliminado sin borrarlo físicamente."""
        self.deleted_at = timezone.now()
        self.save()