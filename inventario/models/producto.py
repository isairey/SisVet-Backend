from django.db import models



class Producto(models.Model):
    nombre = models.CharField(max_length=150, default="sin nombre")
    descripcion = models.TextField(blank=True)
    marca = models.ForeignKey('Marca', on_delete=models.CASCADE)
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=0)
    codigo_barras = models.CharField(max_length=50, blank=True)
    codigo_interno = models.CharField(max_length=50, blank=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete: marcar inactivo, NO eliminar.
        """
        self.activo = False
        self.save(update_fields=["activo"])


    def save(self, *args, **kwargs):
        """
        Normalización automática de campos antes de guardar.

        Responsabilidades:
        - Normalizar formato de texto (Title Case)
        - Limpiar espacios en blanco
        - Verificar alertas después de guardar

        Las validaciones de negocio (stock, precios, duplicados)
        están en ProductoService y se ejecutan desde las Views.
        """
        # Normalizar nombre a Title Case
        if self.nombre:
            self.nombre = self.nombre.strip().title()

        # Normalizar códigos (solo trim, sin title case)
        if self.codigo_barras:
            self.codigo_barras = self.codigo_barras.strip()

        if self.codigo_interno:
            self.codigo_interno = self.codigo_interno.strip()


        # Guardar en base de datos
        super().save(*args, **kwargs)

        # Verificar alertas DESPUÉS de guardar (cuando ya tiene ID)
        self._verificar_alertas()



    def _verificar_alertas(self):
        """
        Verifica y crea/elimina notificaciones después de guardar.
        """
        from inventario.services.notificacion_service import NotificacionService

        notificacion_service = NotificacionService()
        notificacion_service.verificar_alertas_producto(self)


    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"