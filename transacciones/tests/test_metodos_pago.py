import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_listar_metodos_pago(api_client, cliente, metodo_pago):
    api_client.force_authenticate(cliente)
    response = api_client.get("/api/v1/metodos-pago/")
    assert response.status_code == 200