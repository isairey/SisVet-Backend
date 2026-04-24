import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_enviar_factura_email(factura_con_detalles, cliente):
    client = APIClient()
    client.force_authenticate(cliente)

    response = client.post(f"/api/v1/facturas/{factura_con_detalles.id}/enviar-email/")
    assert response.status_code == 200
    assert response.data["mensaje"] == "Factura enviada correctamente."