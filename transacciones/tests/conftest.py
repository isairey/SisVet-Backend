import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from decimal import Decimal


# ============================================
# CLIENTE API
# ============================================
@pytest.fixture
def api_client():
    return APIClient()


# ============================================
# USUARIO / CLIENTE
# ============================================
@pytest.fixture
def cliente(db):
    """
    Crea un usuario normal que funcionará como cliente.
    Compatible con tu modelo Usuario sin first_name/last_name.
    """
    Usuario = get_user_model()
    return Usuario.objects.create_user(
        username="cliente_test",
        email="cliente@test.com",
        password="testpass123",
        nombre="Cliente",
        apellido="Test",
        estado="activo"
    )


@pytest.fixture
def cliente_autenticado(api_client, cliente):
    """
    Autentica al cliente.
    Útil para endpoints donde se requiere login.
    """
    api_client.force_authenticate(user=cliente)
    return api_client


# ============================================
# ESPECIE Y RAZA
# ============================================
@pytest.fixture
def especie(db):
    from mascotas.models import Especie
    return Especie.objects.create(nombre="Perro")


@pytest.fixture
def raza(db, especie):
    from mascotas.models import Raza
    return Raza.objects.create(nombre="Labrador", especie=especie)


# ============================================
# MASCOTA
# ============================================
@pytest.fixture
def mascota(db, cliente, especie, raza):
    from mascotas.models import Mascota
    from usuarios.models import Cliente as ClientePerfil

    # Perfil Cliente (tu modelo usa FK Cliente, NO Usuario)
    perfil = ClientePerfil.objects.create(
        usuario=cliente,
        telefono="123456",
        direccion="Calle 123"
    )

    return Mascota.objects.create(
        cliente=perfil,
        especie=especie,
        raza=raza,
        nombre="Firulais",
        sexo="M"
    )


# ============================================
# SERVICIO
# ============================================
@pytest.fixture
def servicio(db):
    from citas.models import Servicio
    return Servicio.objects.create(
        nombre="Consulta general",
        costo=Decimal("30000.00")
    )


# ============================================
# CITA
# ============================================
@pytest.fixture
def cita(db, mascota, servicio, cliente):
    from citas.models import Cita
    from usuarios.models import UsuarioRol, Rol

    # Crear rol veterinario
    rol, _ = Rol.objects.get_or_create(nombre="veterinario")

    # Crear un usuario veterinario
    Usuario = get_user_model()
    vet = Usuario.objects.create_user(
        username="vet_test",
        email="vet@test.com",
        password="vet123",
        nombre="Vet",
        apellido="Test",
        estado="activo"
    )
    UsuarioRol.objects.create(usuario=vet, rol=rol)

    return Cita.objects.create(
        mascota=mascota,
        veterinario=vet,
        servicio=servicio,
        fecha_hora="2025-01-01T10:00:00"
    )


# ============================================
# CONSULTA
# ============================================
@pytest.fixture
def consulta(db, mascota):
    from consultas.models import Consulta
    from usuarios.models import Veterinario

    # Crear objeto veterinario directo (tu modelo lo usa)
    vet = Veterinario.objects.create(
        usuario=mascota.cliente.usuario,
        licencia="LIC123",
        especialidad="General",
        horario="8-5"
    )

    return Consulta.objects.create(
        mascota=mascota,
        veterinario=vet,
        descripcion_consulta="Dolor de estómago",
        diagnostico="Gastritis"
    )


# ============================================
# MÉTODO DE PAGO
# ============================================
@pytest.fixture
def metodo_pago(db):
    from transacciones.models.metodo_pago import MetodoPago
    return MetodoPago.objects.create(
        nombre="Efectivo",
        codigo="1"
    )


# ============================================
# FACTURA
# ============================================
@pytest.fixture
def factura(db, cliente):
    from transacciones.models.factura import Factura
    return Factura.objects.create(
        cliente=cliente,
        subtotal=Decimal("0.00"),
        impuestos=Decimal("0.00"),
        total=Decimal("0.00"),
        estado="PENDIENTE",
        pagada=False
    )


# ============================================
# PRODUCTO Y DETALLES
# ============================================
@pytest.fixture
def producto(db):
    from inventario.models import Producto, Marca, Categoria

    marca = Marca.objects.create(descripcion="Genérica")
    categoria = Categoria.objects.create(descripcion="Servicios", color="Blanco")

    return Producto.objects.create(
        descripcion="Desparasitación",
        marca=marca,
        categoria=categoria,
        stock=10,
        stock_minimo=1,
        precio_venta=Decimal("50000.00")
    )


@pytest.fixture
def detalle_producto(db, factura, producto):
    from transacciones.models.detalle_factura import DetalleFactura
    return DetalleFactura.objects.create(
        factura=factura,
        producto=producto,
        cantidad=1
    )


# ============================================
# FACTURA CON DETALLES
# ============================================
@pytest.fixture
def factura_con_detalles(factura, detalle_producto):
    """
    Factura con 1 detalle listo para pruebas.
    """
    factura.recalcular_totales()
    return factura


# ============================================
# PAGO
# ============================================
@pytest.fixture
def pago(db, factura, metodo_pago):
    from transacciones.models.pago import Pago
    return Pago.objects.create(
        factura=factura,
        metodo=metodo_pago,
        monto=Decimal("50000.00"),
        aprobado=True,
        referencia="REF123"
    )