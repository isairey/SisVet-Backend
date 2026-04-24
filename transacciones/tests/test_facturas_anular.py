import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_anular_factura(factura, cliente):
    client = APIClient()
    client.force_authenticate(cliente)

    response = client.post(f"/api/v1/facturas/{factura.id}/anular/")
    assert response.status_code == 200
    assert response.data["estado"] == "ANULADA"