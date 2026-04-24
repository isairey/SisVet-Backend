"""
Endpoint temporal para diagnosticar problemas de envío de emails.
⚠️ ELIMINAR DESPUÉS DE RESOLVER EL PROBLEMA
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.conf import settings
import traceback

class TestEmailView(APIView):
    """
    Endpoint temporal para probar el envío de correos.
    ⚠️ ELIMINAR DESPUÉS DE VERIFICAR
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        to_email = request.data.get('email', 'jrodriguez_25@cue.edu.co')
        
        try:
            # Verificar configuración
            config_info = {
                'EMAIL_BACKEND': str(settings.EMAIL_BACKEND),
                'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', 'NOT SET'),
                'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', 'NOT SET'),
                'EMAIL_USE_TLS': getattr(settings, 'EMAIL_USE_TLS', 'NOT SET'),
                'EMAIL_HOST_USER': getattr(settings, 'EMAIL_HOST_USER', 'NOT SET'),
                'EMAIL_HOST_PASSWORD': '***SET***' if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else 'NOT SET',
                'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', 'NOT SET'),
            }
            
            print("=" * 50)
            print("TEST EMAIL - Configuración:")
            for key, value in config_info.items():
                print(f"  {key}: {value}")
            print("=" * 50)
            
            # Intentar enviar correo
            print(f"📧 Intentando enviar correo de prueba a {to_email}...")
            send_mail(
                subject='Test Email desde Render',
                message='Este es un correo de prueba desde Render.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                html_message='<h1>Test Email</h1><p>Este es un correo de prueba desde Render.</p>',
                fail_silently=False,
            )
            
            print(f"✅ Correo de prueba enviado exitosamente a {to_email}")
            
            return Response({
                'success': True,
                'message': f'Correo enviado exitosamente a {to_email}',
                'config': config_info
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            error_details = {
                'error': str(e),
                'error_type': type(e).__name__,
                'traceback': traceback.format_exc(),
                'config': config_info
            }
            
            print("=" * 50)
            print("TEST EMAIL - ERROR:")
            print(f"  Error: {str(e)}")
            print(f"  Tipo: {type(e).__name__}")
            print("  Traceback:")
            print(traceback.format_exc())
            print("=" * 50)
            
            return Response({
                'success': False,
                'message': 'Error al enviar correo',
                'details': error_details
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

