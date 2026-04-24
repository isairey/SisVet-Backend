from django.db import models
from rest_framework.exceptions import ValidationError


class Kardex(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    fecha = models.DateTimeField(auto_now_add=True)
    cantidad = models.IntegerField()
    detalle = models.TextField(blank=True)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='movimientos')

    def __str__(self):
        return f"{self.tipo.capitalize()} - {self.producto.nombre}"

    class Meta:
        verbose_name = "Kardex"
        verbose_name_plural = "Kardex"
        ordering = ['-fecha']

    def delete(self, *args, **kwargs):
        from rest_framework.exceptions import ValidationError
        raise ValidationError("Los movimientos no pueden eliminarse directamente. Deben anularse.")