# tasks.py
from .signals import actualizar_todas_membresias, verificar_membresias_por_vencer


def tarea_actualizar_membresias():
    actualizar_todas_membresias()


def tarea_verificar_vencimientos():
    membresias = verificar_membresias_por_vencer()
    # Aquí podrías agregar lógica para enviar notificaciones
    return len(membresias)
