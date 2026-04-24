"""
Registro views - Manejo completo del flujo de registro con verificación.
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db import transaction
from usuarios.models import Usuario, UsuarioPendiente, Rol, UsuarioRol, Cliente
from usuarios.serializers import (
    RegistroPendienteSerializer,
    CodigoVerificacionSerializer,
    ReenviarCodigoSerializer
)
from notificaciones.patterns.factory import NotificationFactory
from datetime import datetime


class RegistroUsuarioAPIView(APIView):
    """
    API para el registro inicial (Paso 1 de 2).
    
    Guarda los datos en UsuarioPendiente y envía código de verificación.
    
    Endpoint: POST /api/v1/auth/registro/
    Body: {
        "username": "usuario123",
        "email": "user@example.com",
        "password": "Password123!",
        "password_confirm": "Password123!",
        "nombre": "Juan",
        "apellido": "Pérez",
        "telefono": "1234567890",  // opcional
        "direccion": "Calle 123"    // opcional
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegistroPendienteSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            usuario_pendiente = serializer.save()
            
            return Response(
                {
                    "success": True,
                    "message": "Registro inicial exitoso. Revisa tu email para el código de verificación.",
                    "data": {
                        "email": usuario_pendiente.email,
                        "username": usuario_pendiente.username,
                        "code_expires_in_minutes": 20
                    }
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"Error al procesar el registro: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerificarCodigoAPIView(APIView):
    """
    API para verificar el código y completar el registro (Paso 2 de 2).
    
    Crea el Usuario definitivo con todos sus datos asociados (Rol, Cliente).
    
    Endpoint: POST /api/v1/auth/verificar/
    Body: {
        "email": "user@example.com",
        "code": "123456"
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = CodigoVerificacionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # El serializer ya validó todo, obtenemos el usuario pendiente
            usuario_pendiente = serializer.validated_data['usuario_pendiente']
            
            # Crear usuario definitivo con todos sus datos (transacción atómica)
            with transaction.atomic():
                # 1. Crear Usuario usando el método create_user del manager
                # IMPORTANTE: La password ya está hasheada en usuario_pendiente
                usuario = Usuario.objects.create(
                    username=usuario_pendiente.username,
                    email=usuario_pendiente.email,
                    password=usuario_pendiente.password,  # Ya está hasheada
                    nombre=usuario_pendiente.nombre,
                    apellido=usuario_pendiente.apellido,
                    is_active=True,
                    estado='activo'
                )
                
                # 2. Asignar rol de cliente (se crea si no existe)
                rol_cliente, _ = Rol.objects.get_or_create(
                    nombre='cliente',
                    defaults={'descripcion': 'Cliente del sistema'}
                )
                UsuarioRol.objects.create(usuario=usuario, rol=rol_cliente)
                
                # 3. Crear perfil de Cliente con los datos adicionales
                Cliente.objects.create(
                    usuario=usuario,
                    telefono=usuario_pendiente.telefono,
                    direccion=usuario_pendiente.direccion
                )
                
                # 4. Eliminar usuario pendiente (ya fue verificado)
                usuario_pendiente.delete()
            
            # 5. Enviar correo de bienvenida (fuera de la transacción para no bloquear si falla)
            try:
                welcome_notification = NotificationFactory.get_notification(
                    evento="WELCOME_EMAIL",
                    to_email=usuario.email,
                    context={
                        "nombre": usuario.nombre,
                        "username": usuario.username,
                        "email": usuario.email,
                        "anio_actual": datetime.now().year
                    }
                )
                welcome_notification.send()
            except Exception as e:
                # Log del error pero no bloquear la respuesta exitosa
                print(f"Error al enviar correo de bienvenida: {str(e)}")
            
            return Response(
                {
                    "success": True,
                    "message": "¡Cuenta verificada exitosamente! Ya puedes iniciar sesión.",
                    "data": {
                        "username": usuario.username,
                        "email": usuario.email,
                        "nombre_completo": usuario.get_full_name()
                    }
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"Error durante la verificación: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReenviarCodigoAPIView(APIView):
    """
    API para reenviar código de verificación.
    
    Útil cuando el código expiró o el usuario no lo recibió.
    
    Endpoint: POST /api/v1/auth/reenviar-codigo/
    Body: {
        "email": "user@example.com"
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ReenviarCodigoSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            usuario_pendiente = serializer.save()
            
            return Response(
                {
                    "success": True,
                    "message": "Nuevo código de verificación enviado. Revisa tu email.",
                    "data": {
                        "email": usuario_pendiente.email,
                        "code_expires_in_minutes": 20
                    }
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"Error al reenviar código: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )