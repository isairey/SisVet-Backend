from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from abc import ABC, abstractmethod
import threading
import os

class BaseNotification(ABC):
    """
    Clase Base Abstracta (El "Molde").
    Implementa el Patrón Template Method.
    Define el esqueleto del algoritmo ("cómo") para enviar una notificación.
    Su única responsabilidad es definir el algoritmo de envío.
    
    Optimizado para Render:
    - Emails críticos: Intento síncrono con timeout, fallback a asíncrono
    - Emails no críticos: Envío asíncrono para no bloquear requests
    """
    
    def __init__(self, context_data: dict, to_email: str):
        self.context_data = context_data
        self.to_email = to_email
        self._email_sent = False
        self._email_error = None

    @abstractmethod
    def get_subject(self) -> str:
        """Método abstracto: Las subclases DEBEN definir el asunto que tendra el correo"""
        pass

    @abstractmethod
    def get_template_name(self) -> str:
        """Método abstracto: Las subclases DEBEN definir plantilla html que usara el correo."""
        pass

    def build_message_body(self) -> str:
        """Construye el cuerpo del mensaje HTML desde una plantilla."""
        template_name = self.get_template_name()
        return render_to_string(template_name, self.context_data)

    def _send_email_sync(self, subject: str, message_body: str):
        """
        Método privado que envía el correo de forma síncrona.
        """
        try:
            # Log de configuración para debugging
            print(f"📧 Configuración SMTP:")
            print(f"   EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'NOT SET')}")
            print(f"   EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'NOT SET')}")
            print(f"   EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'NOT SET')}")
            print(f"   DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'NOT SET')}")
            print(f"   Enviando a: {self.to_email}")
            
            send_mail(
                subject,
                message_body,
                settings.DEFAULT_FROM_EMAIL,
                [self.to_email],
                html_message=message_body,
                fail_silently=False,
            )
            self._email_sent = True
            print(f"✅ Correo '{subject}' enviado exitosamente a {self.to_email}")
        except Exception as e:
            self._email_error = e
            import traceback
            error_msg = f"❌ Error enviando '{subject}' a {self.to_email}: {e}"
            print(error_msg)
            print(f"❌ Traceback completo:")
            print(traceback.format_exc())
            raise

    def send(self, require_success: bool = False):
        """
        El "Template Method": El algoritmo principal e invariable.
        Construye y envía el email de forma optimizada para Render.
        
        Args:
            require_success: Si es True, intenta síncrono con timeout corto, 
                           luego fallback a asíncrono si no se completa.
                           Si es False, envía asíncrono directamente.
        
        Estrategia para Render:
        - Emails críticos: Intento síncrono con timeout (5s), si no se completa
          lanza thread asíncrono y responde al usuario (el email se enviará en background)
        - Emails no críticos: Asíncrono directo
        """
        subject = self.get_subject()
        message_body = self.build_message_body()
        
        # Para emails críticos, intentar síncrono con timeout corto
        if require_success:
            print(f"📧 Intentando envío síncrono de correo crítico '{subject}' a {self.to_email}...")
            
            # Resetear flags antes de intentar
            self._email_sent = False
            self._email_error = None
            
            # Crear thread para el envío
            email_thread = threading.Thread(
                target=self._send_email_sync,
                args=(subject, message_body),
                daemon=False,  # NO daemon para que no se interrumpa
                name=f"CriticalEmail-{subject[:15]}"
            )
            email_thread.start()
            
            # Esperar máximo 5 segundos (suficiente para SendGrid)
            email_thread.join(timeout=5)
            
            if email_thread.is_alive():
                # El envío aún está en proceso, pero no esperamos más
                # El thread continuará en background y el email se enviará
                print(f"⏳ Envío de correo crítico '{subject}' en proceso (background)...")
                print(f"⚠️ ADVERTENCIA: El thread aún está corriendo, el email puede enviarse en background")
                # No lanzamos error, el email se enviará en background
                return
            elif self._email_sent:
                # El email se envió exitosamente
                print(f"✅ Correo crítico '{subject}' enviado exitosamente")
                return
            elif self._email_error:
                # Hubo un error, lanzarlo
                print(f"❌ ERROR CRÍTICO: {self._email_error}")
                raise self._email_error
            else:
                # Timeout pero no sabemos el estado, asumir que se está enviando
                print(f"⏳ Envío de correo crítico '{subject}' en proceso (timeout)...")
                print(f"⚠️ ADVERTENCIA: Timeout alcanzado, el email puede enviarse en background")
                return
        
        # Para emails no críticos, usar modo asíncrono directo
        use_async = os.getenv('USE_ASYNC_EMAIL', 'True').lower() == 'true'
        
        if use_async:
            thread = threading.Thread(
                target=self._send_email_sync,
                args=(subject, message_body),
                daemon=True,
                name=f"Email-{subject[:15]}"
            )
            thread.start()
        else:
            # Modo síncrono (solo para debugging)
            self._send_email_sync(subject, message_body)