from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Usuario,
    Rol,
    UsuarioRol,
    Cliente,
    Veterinario,
    Practicante,
    ResetPasswordToken,
)

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'nombre', 'apellido', 'estado', 'is_active', 'is_staff')
    list_filter = ('estado', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'nombre', 'apellido')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Información Personal', {'fields': ('nombre', 'apellido', 'estado')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('last_login', 'created_at')})
    )

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol')
    list_filter = ('rol',)
    search_fields = ('usuario__username', 'rol__nombre')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'telefono', 'direccion')

@admin.register(Veterinario)
class VeterinarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'licencia', 'especialidad')
    search_fields = ['nombre', 'apellido', 'email']

@admin.register(Practicante)
class PracticanteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tutor_veterinario', 'universidad', 'periodo_practica')


@admin.register(ResetPasswordToken)
class ResetPasswordTokenAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'token', 'usado', 'expires_at', 'created_at')
    search_fields = ('usuario__username', 'usuario__email', 'token')
    list_filter = ('usado',)