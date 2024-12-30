# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from .models import Membresia


@receiver(post_save, sender=Membresia)
def actualizar_estado_membresia(sender, instance, created, **kwargs):
    """
    Actualiza el estado de la membresía basado en la fecha actual y fecha de fin
    """
    fecha_actual = timezone.now().date()

    # Solo actualizamos si el estado no es CANCELADA
    if instance.estado != 'CANCELADA':
        if fecha_actual > instance.fecha_fin:
            # Si la fecha actual es posterior a la fecha de fin, marcamos como VENCIDA
            if instance.estado != 'VENCIDA':
                instance.estado = 'VENCIDA'
                instance.save()
        else:
            # Si la fecha actual es anterior a la fecha de fin, marcamos como ACTIVA
            if instance.estado != 'ACTIVA':
                instance.estado = 'ACTIVA'
                instance.save()


def verificar_membresias_por_vencer():
    """
    Función para verificar membresías próximas a vencer
    Útil para correr como tarea programada
    """
    fecha_actual = timezone.now().date()
    # Verificamos 7 días hacia adelante
    fecha_limite = fecha_actual + timedelta(days=7)

    membresias_por_vencer = Membresia.objects.filter(
        Q(estado='ACTIVA') &
        Q(fecha_fin__lte=fecha_limite) &
        Q(fecha_fin__gte=fecha_actual)
    )

    return membresias_por_vencer

# Optional: Función para actualizar todas las membresías


def actualizar_todas_membresias():
    """
    Actualiza el estado de todas las membresías
    Útil para correr como tarea programada
    """
    fecha_actual = timezone.now().date()

    # Buscamos membresías vencidas que no estén marcadas como tal
    membresias_vencidas = Membresia.objects.filter(
        ~Q(estado='VENCIDA') &
        ~Q(estado='CANCELADA') &
        Q(fecha_fin__lt=fecha_actual)
    )

    # Actualizamos en bloque
    membresias_vencidas.update(estado='VENCIDA')

    # Buscamos membresías que deberían estar activas
    membresias_activas = Membresia.objects.filter(
        ~Q(estado='ACTIVA') &
        ~Q(estado='CANCELADA') &
        Q(fecha_fin__gte=fecha_actual)
    )

    # Actualizamos en bloque
    membresias_activas.update(estado='ACTIVA')
