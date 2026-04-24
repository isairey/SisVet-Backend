from django.contrib import admin
from django.utils.html import format_html

from mascotas.models import Especie, Raza, Mascota

# Jeronimo Rodriguez - 11/03/2025

class BaseAdmin(admin.ModelAdmin):
    # Exclude audit fields and the UUID `id` so they don't appear in add/change forms
    exclude = ('id', 'created_at', 'updated_at', 'deleted_at')
    # No need to show `id` as readonly; keep other readonly fields here if needed
    readonly_fields = ()
    ordering = ['-id']

@admin.register(Especie)
class EspecieAdmin(BaseAdmin):
    list_display = ('id', 'nombre', 'created_at')
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(Raza)
class RazaAdmin(BaseAdmin):
    list_display = ('id', 'nombre', 'especie', 'created_at')
    list_filter = ('especie',)
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(Mascota)
class MascotaAdmin(BaseAdmin):
    list_display = ('id', 'nombre', 'cliente', 'especie', 'raza', 'sexo', 'peso', 'created_at')
    list_filter = ('especie', 'raza', 'sexo')
    search_fields = ('nombre', 'cliente__usuario__nombre', 'cliente__usuario__apellido')
    ordering = ('nombre',)
