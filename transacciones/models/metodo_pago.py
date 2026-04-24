from django.db import models


class MetodoPago(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    codigo = models.CharField(max_length=30, unique=True)  # ejemplo: PSE, PAYU, STRIPE

    def __str__(self):
        return self.nombre