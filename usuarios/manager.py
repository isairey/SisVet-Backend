from django.contrib.auth.base_user import BaseUserManager

# Jeronimo Rodriguez 10/28/2025 

class UserManager(BaseUserManager):
    """Manager personalizado para el modelo Usuario."""
    
    def create_user(self, username, email, password=None, **extra_fields):
        """Crea y guarda un usuario regular."""
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')
        if not username:
            raise ValueError('El usuario debe tener un nombre de usuario')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        """Crea y guarda un superusuario."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('estado', 'activo')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)