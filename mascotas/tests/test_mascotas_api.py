import pytest
from django.urls import reverse
from rest_framework import status

from mascotas.models import Especie, Raza, Mascota


@pytest.mark.django_db
class TestMascotasAPI:
    def test_list_sin_mascotas_devuelve_mensaje(self, usuario_autenticado):
        """Si el cliente no tiene mascotas, el endpoint devuelve mensaje amigable."""
        api_client = usuario_autenticado

        url = reverse('mascotas-list-create')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        assert response.data['results'] == []

    def test_crear_mascota_exitoso(self, api_client, usuario_cliente):
        """Crear una mascota asociada al cliente autenticado."""
        api_client.force_authenticate(user=usuario_cliente)

        especie = Especie.objects.create(nombre='Perro')
        raza = Raza.objects.create(nombre='Labrador', especie=especie)

        url = reverse('mascotas-list-create')
        datos = {
            'nombre': 'Fido',
            'sexo': 'M',
            'especie': str(especie.id),
            'raza': str(raza.id),
        }

        response = api_client.post(url, datos, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        # representación: cliente es nombre completo
        assert response.data['cliente'] == f"{usuario_cliente.nombre} {usuario_cliente.apellido}"
        assert response.data['nombre'] == 'Fido'

        # Confirmar en DB
        mascota = Mascota.objects.get(id=response.data['id'])
        assert mascota.nombre == 'Fido'

    def test_detalle_actualizar_eliminar_mascota(self, api_client, usuario_cliente, usuario_administrador):
        """Prueba flujo: crear mascota, obtener detalle, actualizar por propietario y bloquear acceso a otro usuario."""
        # Crear especie/raza y mascota
        especie = Especie.objects.create(nombre='Gato')
        raza = Raza.objects.create(nombre='Siamés', especie=especie)

        cliente_usuario = usuario_cliente
        mascota = Mascota.objects.create(
            cliente=cliente_usuario.perfil_cliente,
            especie=especie,
            raza=raza,
            nombre='Michi',
            sexo='H'
        )

        # Propietario puede obtener detalle
        api_client.force_authenticate(user=cliente_usuario)
        url_detail = reverse('mascota-detail', kwargs={'pk': mascota.id})
        resp_get = api_client.get(url_detail)
        assert resp_get.status_code == status.HTTP_200_OK
        assert resp_get.data['nombre'] == 'Michi'

        # Otro usuario autenticado (administrador) NO debe poder acceder al recurso del cliente
        api_client.force_authenticate(user=usuario_administrador)
        resp_get_other = api_client.get(url_detail)
        # La vista filtra por cliente__usuario=request.user, por tanto devuelve 404
        assert resp_get_other.status_code == status.HTTP_404_NOT_FOUND

        # Volver al propietario y actualizar
        api_client.force_authenticate(user=cliente_usuario)
        resp_patch = api_client.patch(url_detail, {'nombre': 'MichiUpdated'}, format='json')
        assert resp_patch.status_code == status.HTTP_200_OK
        mascota.refresh_from_db()
        assert mascota.nombre == 'MichiUpdated'

        # Eliminar
        resp_delete = api_client.delete(url_detail)
        assert resp_delete.status_code in (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK)
        # Confirmar que ya no existe
        with pytest.raises(Mascota.DoesNotExist):
            Mascota.objects.get(id=mascota.id)
