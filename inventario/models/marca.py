from django.db import models
from django.core.exceptions import ValidationError


class Marca(models.Model):
    descripcion = models.CharField(max_length=100, unique=True)

    def save(self, *args, **kwargs):

        # Normalizar a Title Case
        if self.descripcion:
            self.descripcion = self.descripcion.strip().title()

        super().save(*args, **kwargs)

    def clean(self):

        if self.descripcion:
            # Normalizar antes de validar
            self.descripcion = self.descripcion.strip().title()

            # Verificar duplicados (ignorando mayúsculas/minúsculas)
            qs = Marca.objects.filter(descripcion__iexact=self.descripcion)
            if self.pk:
                qs = qs.exclude(pk=self.pk)

            if qs.exists():
                raise ValidationError({
                    'descripcion': 'Ya existe una marca con este nombre.'
                })

    def __str__(self):
        return self.descripcion

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"