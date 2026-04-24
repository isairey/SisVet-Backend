import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_listar_facturas_vacio(api_client, cliente):
    api_client.force_authenticate(cliente)
    response = api_client.get("/api/v1/facturas/")
    assert response.status_code == 200

@pytest.mark.django_db
def test_crear_factura_basica(cliente):
    client = APIClient()
    client.force_authenticate(user=cliente)

    payload = {
        "detalles": [],    # evita validaciones que exijan detalles
    }

    response = client.post("/api/v1/facturas/", payload, format='json')
    assert response.status_code == 201
    assert response.data["cliente"] == cliente.id