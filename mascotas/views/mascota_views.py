from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from mascotas.models import Mascota, Especie, Raza
from mascotas.serializers.mascota_serializer import (
    MascotaSerializer,
    EspecieSerializer,
    RazaSerializer,
)
from mascotas.serializers.especie_raza_serializer import (
    EspecieCreateSerializer,
    RazaCreateSerializer,
)
from mascotas.permissions import MascotaListPermission

"""
Vistas (API) para el módulo de mascotas.

Contiene las vistas para listar/crear mascotas y para obtener/actualizar/eliminar
una mascota concreta del cliente autenticado. Las vistas están protegidas y
requieren autenticación JWT (o el sistema de autenticación configurado en el proyecto).

Responden con mensajes amigables cuando no hay resultados o cuando el recurso
no pertenece al usuario autenticado.
"""

# Jeronimo Rodriguez - 11/03/2025

def _obtener_rol_usuario(usuario):
    """
    Obtiene el primer rol asociado al usuario.
    
    Args:
        usuario: Instancia de Usuario
        
    Returns:
        str: nombre del rol (ej: 'administrador', 'veterinario', 'recepcionista', 'cliente')
             o None si no tiene rol asignado
    """
    usuario_rol = usuario.usuario_roles.first()
    if usuario_rol:
        return usuario_rol.rol.nombre
    return None


class MascotaListCreateView(generics.ListCreateAPIView):
    """
    Endpoint para listar y registrar mascotas según el rol del usuario.
    
    - GET: Lista las mascotas según el rol:
        * ADMIN, VETERINARIO, RECEPCIONISTA: ven todas las mascotas.
        * CLIENTE: solo ve sus propias mascotas.
    - POST: Crea una nueva mascota asociada al cliente autenticado.
    """
    serializer_class = MascotaSerializer
    permission_classes = [MascotaListPermission]

    def get_queryset(self):
        """
        Filtra las mascotas según el rol del usuario autenticado y los filtros solicitados.
        """
        usuario = self.request.user
        rol = _obtener_rol_usuario(usuario)

        roles_acceso_total = ['administrador', 'veterinario', 'recepcionista']

        if rol in roles_acceso_total:
            queryset = Mascota.objects.all()
        elif rol == 'cliente':
            queryset = Mascota.objects.filter(cliente__usuario=usuario)
        else:
            queryset = Mascota.objects.none()

        search = self.request.query_params.get('search')
        if search:
            search = search.strip()
            if search:
                queryset = queryset.filter(
                    Q(nombre__icontains=search) |
                    Q(cliente__usuario__nombre__icontains=search) |
                    Q(cliente__usuario__apellido__icontains=search) |
                    Q(especie__nombre__icontains=search) |
                    Q(raza__nombre__icontains=search)
                )

        especie_param = self.request.query_params.get('especie')
        if especie_param:
            try:
                especie_id = int(especie_param)
            except (TypeError, ValueError):
                raise ValidationError({'especie': 'Debe ser un ID numérico válido.'})
            queryset = queryset.filter(especie_id=especie_id)

        raza_param = self.request.query_params.get('raza')
        if raza_param:
            try:
                raza_id = int(raza_param)
            except (TypeError, ValueError):
                raise ValidationError({'raza': 'Debe ser un ID numérico válido.'})
            queryset = queryset.filter(raza_id=raza_id)

        return queryset

    def perform_create(self, serializer):
        """Guarda la mascota asociada al cliente."""
        serializer.save()

    def list(self, request, *args, **kwargs):
        """Retorna la lista de mascotas según el rol del usuario.

        Si no hay mascotas disponibles para el rol, devuelve un mensaje
        claro para facilitar la interpretación desde clientes como Postman
        o aplicaciones frontend.
        """
        conjunto_mascotas = self.get_queryset()

        if not conjunto_mascotas.exists():
            return Response({
                'message': 'No hay mascotas disponibles para tu rol.',
                'results': []
            }, status=status.HTTP_200_OK)

        return super().list(request, *args, **kwargs)


class EspecieListCreateView(generics.ListCreateAPIView):
    """
    Endpoint para listar y crear especies.
    
    - GET: Lista todas las especies disponibles (público, sin autenticación).
    - POST: Crea una nueva especie (requiere autenticación y rol administrativo).
    """

    queryset = Especie.objects.all()
    permission_classes = [AllowAny]  # GET es público
    pagination_class = None

    def get_serializer_class(self):
        """Usa serializer de escritura para POST, de lectura para GET."""
        if self.request.method == 'POST':
            return EspecieCreateSerializer
        return EspecieSerializer

    def get_permissions(self):
        """Aplica permisos diferentes según el método HTTP."""
        if self.request.method == 'POST':
            # POST requiere autenticación y rol administrativo
            return [IsAuthenticated()]
        # GET es público
        return [AllowAny()]

    def perform_create(self, serializer):
        """Valida permisos antes de crear."""
        usuario = self.request.user
        rol = _obtener_rol_usuario(usuario)
        roles_permitidos = ['administrador', 'veterinario', 'recepcionista']

        if not usuario.is_superuser and rol not in roles_permitidos:
            raise ValidationError(
                "Solo administradores, veterinarios y recepcionistas pueden crear especies."
            )
        serializer.save()


class RazaListCreateView(generics.ListCreateAPIView):
    """
    Endpoint para listar y crear razas.
    
    - GET: Lista las razas filtradas por especie (parámetro obligatorio `especie`).
           Público, sin autenticación.
    - POST: Crea una nueva raza (requiere autenticación y rol administrativo).
    """

    permission_classes = [AllowAny]  # GET es público
    pagination_class = None

    def get_serializer_class(self):
        """Usa serializer de escritura para POST, de lectura para GET."""
        if self.request.method == 'POST':
            return RazaCreateSerializer
        return RazaSerializer

    def get_permissions(self):
        """Aplica permisos diferentes según el método HTTP."""
        if self.request.method == 'POST':
            # POST requiere autenticación y rol administrativo
            return [IsAuthenticated()]
        # GET es público
        return [AllowAny()]

    def get_queryset(self):
        """Filtra razas por especie para GET."""
        especie_param = self.request.query_params.get("especie")
        
        # Para POST, no se requiere el parámetro especie (viene en el body)
        if self.request.method == 'POST':
            return Raza.objects.all()
        
        # Para GET, el parámetro especie es obligatorio
        if especie_param is None:
            raise ValidationError({"especie": "El parámetro especie es obligatorio."})

        try:
            especie_id = int(especie_param)
        except (TypeError, ValueError):
            raise ValidationError({"especie": "Debe ser un ID numérico válido."})

        queryset = Raza.objects.filter(especie_id=especie_id)
        if not queryset.exists() and not Especie.objects.filter(id=especie_id).exists():
            raise NotFound(detail="La especie indicada no existe.")
        return queryset

    def perform_create(self, serializer):
        """Valida permisos antes de crear."""
        usuario = self.request.user
        rol = _obtener_rol_usuario(usuario)
        roles_permitidos = ['administrador', 'veterinario', 'recepcionista']

        if not usuario.is_superuser and rol not in roles_permitidos:
            raise ValidationError(
                "Solo administradores, veterinarios y recepcionistas pueden crear razas."
            )
        serializer.save()


class MascotaRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    Permite consultar, actualizar o eliminar una mascota específica del cliente autenticado.
    """
    serializer_class = MascotaSerializer
    permission_classes = [MascotaListPermission]

    def get_queryset(self):
        usuario = self.request.user
        rol = _obtener_rol_usuario(usuario)
        roles_acceso_total = ['administrador', 'veterinario', 'recepcionista']

        if rol in roles_acceso_total:
            return Mascota.objects.all()
        return Mascota.objects.filter(cliente__usuario=usuario)

    def get_object(self):
        """Obtiene la mascota solicitada y maneja errores de forma amigable.

        - Valida que el parámetro de búsqueda esté presente en la URL.
        - Intenta recuperar la mascota solo dentro del conjunto del cliente
          autenticado (evita que un usuario acceda a mascotas de otro).
        - Si no se encuentra, lanza `NotFound` con un mensaje claro.
        """

        # Campo por el cual se hará la búsqueda (por defecto 'pk' o lo
        # que haya sido configurado en la vista).
        campo_busqueda = self.lookup_field
        argumento_url_busqueda = self.lookup_url_kwarg or campo_busqueda
        valor_busqueda = self.kwargs.get(argumento_url_busqueda)

        # Si no se proporcionó el valor en la URL, mostrar un error claro.
        if valor_busqueda is None:
            raise NotFound(detail='Se requiere el identificador de la mascota en la URL.')

        try:
            # Buscar la mascota únicamente dentro del queryset del cliente
            # autenticado para asegurar que el usuario no accede a recursos
            # de terceros.
            mascota = self.get_queryset().get(**{campo_busqueda: valor_busqueda})
        except Mascota.DoesNotExist:
            # Mensaje claro para el cliente indicando que no se encontró la mascota
            # o que no pertenece al usuario autenticado.
            raise NotFound(detail='Mascota no encontrada o no pertenece al usuario autenticado.')

        # Ejecutar los chequeos de permisos estándar (si se hubieran definido)
        self.check_object_permissions(self.request, mascota)
        return mascota