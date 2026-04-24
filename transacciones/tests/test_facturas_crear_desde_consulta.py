import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_crear_factura_desde_consulta(consulta, cliente):
    client = APIClient()
    client.force_authenticate(cliente)

    response = client.post(f"/api/v1/facturas/crear-desde-consulta/{consulta.id}/")
    assert response.status_code == 201
    assert response.data["cliente"] == cliente.id