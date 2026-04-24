"""
Pruebas unitarias para el endpoint de perfil de usuario.

Autor: Jeronimo Rodríguez Sepúlveda
Fecha: 2025-11-10

Este módulo contiene las pruebas para el endpoint GET/PUT/PATCH /api/v1/perfil/,
que permite a los usuarios autenticados visualizar y actualizar su perfil.
"""

import pytest


@pytest.mark.django_db
class TestPerfilUsuario:
    """
    Clase de pruebas para el endpoint de perfil de usuario.
    
    Valida que los usuarios autenticados puedan visualizar y actualizar
    su información de perfil correctamente.
    """
    
    def test_obtener_perfil_exitoso(self, usuario_autenticado, usuario_cliente):
        """
        Prueba que un usuario autenticado puede obtener su perfil.
        
        Valida:
        - Código de respuesta 200 (OK)
        - Estructura correcta del JSON de respuesta
        - Información completa del usuario
        - Roles asignados
        - Perfil de cliente si existe
        """
        from django.urls import reverse
        from rest_framework import status
        
        url = reverse('perfil')
        
        response = usuario_autenticado.get(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar estructura de la respuesta
        assert 'id' in response.data
        assert 'username' in response.data
        assert 'email' in response.data
        assert 'nombre' in response.data
        assert 'apellido' in response.data
        assert 'estado' in response.data
        assert 'roles' in response.data
        assert 'created_at' in response.data
        
        # Validar datos del usuario
        assert response.data['id'] == usuario_cliente.id
        assert response.data['username'] == usuario_cliente.username
        assert response.data['email'] == usuario_cliente.email
        assert response.data['nombre'] == usuario_cliente.nombre
        assert response.data['apellido'] == usuario_cliente.apellido
        
        # Validar roles
        assert isinstance(response.data['roles'], list)
        assert len(response.data['roles']) > 0
        
        # Validar perfil de cliente
        assert 'perfil_cliente' in response.data
        if response.data['perfil_cliente']:
            assert 'telefono' in response.data['perfil_cliente']
            assert 'direccion' in response.data['perfil_cliente']
    
    def test_obtener_perfil_sin_autenticacion(self, api_client):
        """
        Prueba que obtener el perfil requiere autenticación.
        
        Valida:
        - Código de respuesta 401 (UNAUTHORIZED)
        """
        from django.urls import reverse
        from rest_framework import status
        
        url = reverse('perfil')
        
        response = api_client.get(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_actualizar_perfil_put_exitoso(self, usuario_autenticado, usuario_cliente):
        """
        Prueba que un usuario puede actualizar su perfil con PUT.
        
        Valida:
        - Código de respuesta 200 (OK)
        - Actualización correcta de los datos
        - Actualización del perfil de cliente
        """
        from django.urls import reverse
        from rest_framework import status
        
        url = reverse('perfil')
        datos_actualizacion = {
            'nombre': 'Nombre Actualizado',
            'apellido': 'Apellido Actualizado',
            'email': 'nuevo_email@test.com',
            'perfil_cliente': {
                'telefono': '9876543210',
                'direccion': 'Nueva Dirección Actualizada'
            }
        }
        
        response = usuario_autenticado.put(url, datos_actualizacion, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar datos actualizados en la respuesta
        assert response.data['nombre'] == datos_actualizacion['nombre']
        assert response.data['apellido'] == datos_actualizacion['apellido']
        assert response.data['email'] == datos_actualizacion['email']
        
        # Validar actualización en base de datos
        usuario_cliente.refresh_from_db()
        assert usuario_cliente.nombre == datos_actualizacion['nombre']
        assert usuario_cliente.apellido == datos_actualizacion['apellido']
        assert usuario_cliente.email == datos_actualizacion['email']
        
        # Validar actualización del perfil de cliente
        usuario_cliente.perfil_cliente.refresh_from_db()
        assert usuario_cliente.perfil_cliente.telefono == datos_actualizacion['perfil_cliente']['telefono']
        assert usuario_cliente.perfil_cliente.direccion == datos_actualizacion['perfil_cliente']['direccion']
    
    def test_actualizar_perfil_patch_exitoso(self, usuario_autenticado, usuario_cliente):
        """
        Prueba que un usuario puede actualizar parcialmente su perfil con PATCH.
        
        Valida:
        - Código de respuesta 200 (OK)
        - Actualización parcial correcta
        - Campos no enviados no se modifican
        """
        from django.urls import reverse
        from rest_framework import status
        
        nombre_original = usuario_cliente.nombre
        email_original = usuario_cliente.email
        
        url = reverse('perfil')
        datos_actualizacion_parcial = {
            'apellido': 'Apellido Parcialmente Actualizado'
        }
        
        response = usuario_autenticado.patch(url, datos_actualizacion_parcial, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar datos actualizados
        assert response.data['apellido'] == datos_actualizacion_parcial['apellido']
        
        # Validar que campos no enviados no se modificaron
        usuario_cliente.refresh_from_db()
        assert usuario_cliente.nombre == nombre_original
        assert usuario_cliente.email == email_original
    
    def test_actualizar_perfil_campos_readonly_no_se_modifican(self, usuario_autenticado, usuario_cliente):
        """
        Prueba que los campos de solo lectura no se pueden modificar.
        
        Valida:
        - Campos como 'id', 'username', 'created_at' no se modifican
        - Estos campos están marcados como read_only en el serializer
        """
        from django.urls import reverse
        from rest_framework import status
        
        id_original = usuario_cliente.id
        username_original = usuario_cliente.username
        created_at_original = usuario_cliente.created_at
        
        url = reverse('perfil')
        datos_intento_modificacion = {
            'id': 99999,
            'username': 'nuevo_username',
            'created_at': '2020-01-01T00:00:00Z',
            'nombre': 'Nombre Actualizado'
        }
        
        response = usuario_autenticado.patch(url, datos_intento_modificacion, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar que los campos read_only no se modificaron
        usuario_cliente.refresh_from_db()
        assert usuario_cliente.id == id_original
        assert usuario_cliente.username == username_original
        assert usuario_cliente.created_at == created_at_original
        
        # Validar que el campo modificable sí se actualizó
        assert usuario_cliente.nombre == datos_intento_modificacion['nombre']
    
    def test_actualizar_perfil_email_invalido(self, usuario_autenticado):
        """
        Prueba que la actualización falla con un email inválido.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST)
        - Mensaje de error apropiado
        """
        from django.urls import reverse
        from rest_framework import status
        
        url = reverse('perfil')
        datos_invalidos = {
            'email': 'email_invalido'
        }
        
        response = usuario_autenticado.patch(url, datos_invalidos, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Validar mensaje de error
        assert 'email' in response.data
    
    def test_actualizar_perfil_email_duplicado(self, usuario_autenticado, usuario_administrador):
        """
        Prueba que la actualización falla si el email ya está en uso.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST)
        - Mensaje de error indicando que el email ya está en uso
        """
        from django.urls import reverse
        from rest_framework import status
        
        url = reverse('perfil')
        datos_duplicado = {
            'email': usuario_administrador.email
        }
        
        response = usuario_autenticado.patch(url, datos_duplicado, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Validar mensaje de error
        assert 'email' in response.data
    
    def test_perfil_incluye_perfil_veterinario(self, api_client, usuario_veterinario):
        """
        Prueba que el perfil de un veterinario incluye su perfil extendido.
        
        Valida:
        - El perfil incluye información del perfil_veterinario
        - Campos como licencia, especialidad, horario están presentes
        """
        from django.urls import reverse
        from rest_framework import status
        
        api_client.force_authenticate(user=usuario_veterinario)
        url = reverse('perfil')
        
        response = api_client.get(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar perfil de veterinario
        assert 'perfil_veterinario' in response.data
        if response.data['perfil_veterinario']:
            assert 'licencia' in response.data['perfil_veterinario']
            assert 'especialidad' in response.data['perfil_veterinario']
            assert 'horario' in response.data['perfil_veterinario']
    
    def test_actualizar_perfil_cliente_telefono_y_direccion(self, usuario_autenticado, usuario_cliente):
        """
        Prueba que se pueden actualizar teléfono y dirección del perfil de cliente.
        
        Valida:
        - Actualización exitosa de campos del perfil de cliente
        - Los cambios se reflejan en la base de datos
        """
        from django.urls import reverse
        from rest_framework import status
        
        url = reverse('perfil')
        datos_actualizacion = {
            'perfil_cliente': {
                'telefono': '5551234567',
                'direccion': 'Calle Nueva 123'
            }
        }
        
        response = usuario_autenticado.patch(url, datos_actualizacion, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar actualización en base de datos
        usuario_cliente.perfil_cliente.refresh_from_db()
        assert usuario_cliente.perfil_cliente.telefono == datos_actualizacion['perfil_cliente']['telefono']
        assert usuario_cliente.perfil_cliente.direccion == datos_actualizacion['perfil_cliente']['direccion']
    
    def test_perfil_retorna_roles_correctos(self, usuario_autenticado, usuario_cliente, rol_cliente):
        """
        Prueba que el perfil retorna los roles correctos del usuario.
        
        Valida:
        - Los roles se incluyen en la respuesta
        - Los roles son correctos según el usuario
        """
        from django.urls import reverse
        from rest_framework import status
        
        url = reverse('perfil')
        
        response = usuario_autenticado.get(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar roles
        assert 'roles' in response.data
        assert isinstance(response.data['roles'], list)
        # Verificar que el rol de cliente está presente
        roles_nombres = [rol.lower() if isinstance(rol, str) else rol.get('nombre', '').lower() for rol in response.data['roles']]
        assert 'cliente' in roles_nombres or any('cliente' in str(rol).lower() for rol in response.data['roles'])

