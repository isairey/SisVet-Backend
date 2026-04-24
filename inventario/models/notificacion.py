from django.db import models
from django.utils import timezone


class Notificacion(models.Model):
    MODULOS = [
        ("inventario", "Inventario"),
    ]

    NIVELES = [
        ("info", "Info"),
        ("warning", "Advertencia"),
        ("error", "Crítico"),
    ]

    titulo = models.CharField(max_length=150)
    mensaje = models.TextField()
    modulo = models.CharField(max_length=50, choices=MODULOS, default="inventario")
    nivel = models.CharField(max_length=20, choices=NIVELES, default="info")
    fecha = models.DateTimeField(default=timezone.now)
    leida = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.modulo.upper()}] {self.titulo}"

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-fecha']