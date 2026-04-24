import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_obtener_detalle_factura(factura):
    client = APIClient()
    # autenticar con el usuario asociado a la factura
    client.force_authenticate(user=factura.cliente)

    response = client.get(f"/api/v1/facturas/{factura.id}/")
    assert response.status_code == 200
    assert response.data["id"] == factura.id