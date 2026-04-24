from django.contrib import admin

from django.contrib import admin
from .models import Servicio, Cita

# Registramos el modelo Servicio para que aparezca en el admin
@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'costo', 'id')
    search_fields = ('nombre',)

# También registraremos Cita, solo para poder verlas
@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('mascota', 'veterinario', 'servicio', 'fecha_hora', 'estado')
    list_filter = ('estado', 'veterinario')
    search_fields = ('mascota__nombre', 'veterinario__nombre')