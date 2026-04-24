import django.dispatch

"""
Define las señales personalizadas (los "eventos" o "gritos")
que la app 'citas' enviará.
"""
cita_agendada_signal = django.dispatch.Signal()
cita_cancelada_signal = django.dispatch.Signal()
cita_reagendada_signal = django.dispatch.Signal()