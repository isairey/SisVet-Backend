from django.db import models
from django.core.exceptions import ValidationError


class Categoria(models.Model):
    descripcion = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=20, blank=True)

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
            qs = Categoria.objects.filter(descripcion__iexact=self.descripcion)
            if self.pk:
                qs = qs.exclude(pk=self.pk)

            if qs.exists():
                raise ValidationError({
                    'descripcion': 'Ya existe una categoría con este nombre.'
                })

    def __str__(self):
        return self.descripcion

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"