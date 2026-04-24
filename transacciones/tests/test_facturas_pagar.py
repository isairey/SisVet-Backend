import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_pagar_factura(factura_con_detalles, metodo_pago, cliente):
    client = APIClient()
    client.force_authenticate(cliente)

    payload = {
        "metodo_pago": metodo_pago.id,
        "monto": factura_con_detalles.total
    }

    response = client.post(f"/api/v1/facturas/{factura_con_detalles.id}/pagar/", payload)
    assert response.status_code == 200
    assert response.data["estado"] == "PAGADA"