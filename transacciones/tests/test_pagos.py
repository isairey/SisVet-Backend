import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_crear_pago(factura, metodo_pago, cliente):
    client = APIClient()
    client.force_authenticate(cliente)

    payload = {
        "factura": factura.id,
        "metodo": metodo_pago.id,
        "monto": 50000
    }

    response = client.post("/api/v1/pagos/", payload)
    assert response.status_code == 201
    assert response.data["factura"] == factura.id