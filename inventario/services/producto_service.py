from inventario.services.normalizacion_service import NormalizacionService
from inventario.validators.producto_validator import ProductoValidator
from inventario.services.notificacion_service import NotificacionService


class ProductoService:

    def __init__(self):
        self.normalizacion = NormalizacionService()
        self.validator = ProductoValidator()
        self.notificaciones = NotificacionService()

    def normalizar_datos_producto(self, data: dict) -> dict:

        datos = {}

        if data.get("nombre"):
            datos["nombre"] = self.normalizacion.normalizar_texto(data["nombre"])

        if data.get("codigo_barras"):
            datos["codigo_barras"] = self.normalizacion.normalizar_codigo(data["codigo_barras"])

        if data.get("codigo_interno"):
            datos["codigo_interno"] = self.normalizacion.normalizar_codigo(data["codigo_interno"])

        return datos

    def validar_datos_producto(self, data: dict, producto_id=None) -> dict:

        # Normalizar texto y códigos
        nombre = self.normalizacion.normalizar_texto(data.get("nombre", ""))
        codigo_barras = (
            self.normalizacion.normalizar_codigo(data.get("codigo_barras"))
            if data.get("codigo_barras") else None
        )
        codigo_interno = (
            self.normalizacion.normalizar_codigo(data.get("codigo_interno"))
            if data.get("codigo_interno") else None
        )

        # Convertir stock a enteros
        try:
            stock = int(data.get("stock", 0) or 0)
            stock_minimo = int(data.get("stock_minimo", 0) or 0)
        except ValueError:
            return {"mensaje": "El stock debe ser un número entero"}

        # Convertir precios a float
        try:
            precio_compra = float(data.get("precio_compra", 0) or 0)
            precio_venta = float(data.get("precio_venta", 0) or 0)
        except ValueError:
            return {"mensaje": "Los precios deben ser números válidos"}

        # Validar nombre requerido
        if not nombre:
            return {"mensaje": "El nombre es requerido", "campo": "nombre"}

        # Validaciones únicas
        try:
            self.validator.validar_nombre_unico(nombre, producto_id)
        except Exception as e:
            return {"mensaje": str(e), "campo": "nombre"}

        try:
            self.validator.validar_codigo_barras_unico(codigo_barras, producto_id)
        except Exception as e:
            return {"mensaje": str(e), "campo": "codigo_barras"}

        try:
            self.validator.validar_codigo_interno_unico(codigo_interno, producto_id)
        except Exception as e:
            return {"mensaje": str(e), "campo": "codigo_interno"}

        # Validación de stock inicial
        try:
            self.validator.validar_stock_inicial(stock, stock_minimo)
        except Exception as e:
            return {"mensaje": str(e), "campo": "stock"}

        # Validación de precios
        try:
            self.validator.validar_precios(precio_compra, precio_venta)
        except Exception as e:
            return {"mensaje": str(e), "campo": "precio_compra"}

        return {}

    def save_producto(self, obj, data: dict, change=False) -> dict:
        """
        Crea o actualiza un producto, normalizando, validando y generando notificación INFO.
        `obj` es la instancia del producto (nuevo o existente)
        `data` son los datos para actualizar
        `change` indica si es actualización (True) o creación (False)
        """
        # Normalizar y validar
        datos_normalizados = self.normalizar_datos_producto(data)
        errores = self.validar_datos_producto(datos_normalizados, getattr(obj, "id", None))
        if errores:
            return {"success": False, "errores": errores}

        # Asignar datos al objeto
        for key, value in datos_normalizados.items():
            setattr(obj, key, value)

        # Guardar el objeto (ajustar según tu ORM)
        obj.save()

        # Notificación INFO
        if change:
            self.notificaciones.crear_info(
                titulo=f"Producto actualizado: {obj.nombre}",
                mensaje="El producto fue modificado desde el administrador."
            )
        else:
            self.notificaciones.crear_info(
                titulo=f"Producto creado: {obj.nombre}",
                mensaje="Se creó un nuevo producto en el sistema."
            )

        return {"success": True, "producto": obj}
