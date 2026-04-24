"""
Patrón Factory Method aplicado a la creación de usuarios por rol.

Este patrón permite instanciar subtipos de usuario (Cliente, Veterinario, Practicante)
sin acoplar el código cliente a las clases concretas.
"""

class Usuario:
    """Clase base para usuarios."""
    def __init__(self, nombre, documento):
        self.nombre = nombre
        self.documento = documento

class Cliente(Usuario):
    """Usuario tipo Cliente."""
    pass

class Veterinario(Usuario):
    """Usuario tipo Veterinario."""
    def __init__(self, nombre, documento, licencia):
        super().__init__(nombre, documento)
        self.licencia = licencia

class Practicante(Usuario):
    """Usuario tipo Practicante."""
    def __init__(self, nombre, documento, universidad):
        super().__init__(nombre, documento)
        self.universidad = universidad

class UsuarioFactory:
    """
    Factory Method para crear instancias del modelo `Usuario` según el rol.

    Esta implementación crea objetos del modelo Django `Usuario` (vía
    `Usuario.objects.create_user`) en lugar de clases de ejemplo, de modo que
    sea compatible con el resto del sistema (serializers y vistas).
    """
    def crear_usuario(self, rol, data: dict):
        """Crea y retorna una instancia de `usuarios.models.Usuario`.

        Args:
            rol (str): Nombre del rol principal ('cliente', 'veterinario', 'practicante', 'administrador', ...)
            data (dict): Diccionario con los campos del usuario (username, email, nombre, apellido, estado, ...)

        Returns:
            Usuario: instancia creada (sin contraseña establecida si no se pasó).
        """
        from usuarios.models import Usuario

        # Campos esperados por el manager/create_user
        user_fields = {
            'username': data.get('username'),
            'email': data.get('email'),
            'nombre': data.get('nombre'),
            'apellido': data.get('apellido'),
            'estado': data.get('estado', 'activo'),
        }

        # Crear usuario sin contraseña (será asignada por quien invoca)
        usuario = Usuario.objects.create_user(password=None, **{k: v for k, v in user_fields.items() if v is not None})

        # Ajustes por rol (por ejemplo, marcar staff para administradores)
        if rol in ('administrador', 'admin'):
            usuario.is_staff = True
            usuario.save()

        return usuario

# Ejemplo de uso:
def demo():
    data = {'rol': 'veterinario', 'nombre': 'Ana', 'documento': '123', 'licencia': 'VET-001'}
    usuario = UsuarioFactory.create_usuario(data)
    print(type(usuario), usuario.__dict__)
