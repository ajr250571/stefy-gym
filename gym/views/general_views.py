from multiprocessing import Value
from django.utils import timezone
from django.db.models.base import Model as Model
from django.shortcuts import get_object_or_404, redirect, render
from gym.models import Asistencia, Membresia
from django.views.generic import View, ListView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
from django.db.models import Count, F, Value
from django.db.models.functions import Concat
from ..filters import AsistenciaFilter
from django_filters.views import FilterView
from django.http import QueryDict
from ..forms import DynamicFilterForm
from functools import reduce
import operator


class AdvancedFilterListView(ListView):
    template_name = ''
    paginate_by = 20
    model = None  # Especificar en la implementación concreta

    def get_queryset(self):
        queryset = super().get_queryset()
        filters = self.request.GET.getlist('filters')

        if filters:
            q_objects = []
            for filter_data in filters:
                if isinstance(filter_data, str):
                    filter_dict = QueryDict(filter_data)
                else:
                    filter_dict = filter_data
                form = DynamicFilterForm(self.model, data=filter_dict)
                if form.is_valid():
                    q_objects.append(form.get_filter())

            if q_objects:
                queryset = queryset.filter(reduce(operator.and_, q_objects))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = DynamicFilterForm(self.model)

        current_filters = []
        filters = self.request.GET.getlist('filters')
        for filter_data in filters:
            if isinstance(filter_data, str):
                filter_dict = QueryDict(filter_data)
            else:
                filter_dict = filter_data
            filter_form = DynamicFilterForm(self.model, data=filter_dict)
            if filter_form.is_valid():
                current_filters.append(filter_form)

        context['current_filters'] = current_filters
        return context


class enviar_whatsapp(View):
    def get(self, request, membresia_id):
        Membresia.enviar_whatsapp(membresia_id)
        return redirect('membresia_list')


def enviar_whatsapp_membresias_vencidas():
    """
    Envía mensajes de WhatsApp a todos los socios con membresías vencidas.
    Returns:
        tuple: (exitosos, fallidos, total)
            - exitosos: número de mensajes enviados correctamente
            - fallidos: número de mensajes que fallaron
            - total: total de membresías procesadas
    """
    # Obtener todas las membresías vencidas
    membresias_vencidas = Membresia.objects.filter(
        estado='VENCIDA',
        socio__telefono__isnull=False  # Solo socios con teléfono registrado
    ).select_related('socio', 'plan')

    exitosos = 0
    fallidos = 0
    total = membresias_vencidas.count()

    for membresia in membresias_vencidas:
        try:
            resultado = Membresia.enviar_whatsapp(membresia.id)  # type: ignore
            if resultado:
                exitosos += 1
            else:
                fallidos += 1
            # Esperar 20 segundos entre mensajes para evitar bloqueos
            # time.sleep(20)
        except Exception as e:
            print(f"Error al procesar membresía {
                membresia.id}: {str(e)}")  # type: ignore
            fallidos += 1

    return exitosos, fallidos, total


def enviar_whatsapp_membresias_por_vencer(dias_anticipacion=7):
    """
    Envía mensajes de WhatsApp a socios cuyas membresías están por vencer en los próximos días.

    Args:
        dias_anticipacion (int): Días de anticipación para el aviso

    Returns:
        tuple: (exitosos, fallidos, total)
    """
    fecha_limite = timezone.now().date() + timezone.timedelta(days=dias_anticipacion)

    membresias_por_vencer = Membresia.objects.filter(
        estado='ACTIVA',
        fecha_fin__lte=fecha_limite,
        fecha_fin__gt=timezone.now().date(),
        socio__telefono__isnull=False
    ).select_related('socio', 'plan')

    exitosos = 0
    fallidos = 0
    total = membresias_por_vencer.count()

    for membresia in membresias_por_vencer:
        try:
            # Modificar el mensaje para estos casos
            dias_restantes = (membresia.fecha_fin - timezone.now().date()).days
            telefono = membresia.socio.telefono
            mensaje = (
                f"Hola {membresia.socio.nombre}!\n"
                f"Te recordamos que tu membresía del plan {
                    membresia.plan.nombre} "
                f"vencerá en {
                    dias_restantes} días ({membresia.fecha_fin.strftime('%d/%m/%Y')}).\n"
                "Contacta con nosotros para renovarla."
            )
            if telefono is None:
                continue

            Membresia.enviar_whatsapp(membresia.id)    # type: ignore
            exitosos += 1
            # time.sleep(20)
        except Exception as e:
            print(f"Error al procesar membresía {
                membresia.id}: {str(e)}")  # type: ignore
            fallidos += 1

    return exitosos, fallidos, total


class whatsapp_vencidas(View):
    def get(self, request):
        exitosos, fallidos, total = enviar_whatsapp_membresias_vencidas()
        return redirect('membresia_list')


class whatsapp_por_vencer(View):
    def get(self, request):
        exitosos, fallidos, total = enviar_whatsapp_membresias_por_vencer()
        return redirect('membresia_list')


class enviar_email(View):
    def get(self, request, membresia_id):
        Membresia.enviar_email(membresia_id)
        return redirect('membresia_list')


def enviar_correo_membresias_vencidas():
    membresias_vencidas = Membresia.objects.filter(
        estado='VENCIDA',
        socio__email__isnull=False  # Solo socios con email registrado
    ).select_related('socio', 'plan')

    exitosos = 0
    fallidos = 0
    total = membresias_vencidas.count()

    for membresia in membresias_vencidas:
        try:
            resultado = Membresia.enviar_email(membresia.id)  # type: ignore
            if resultado:
                exitosos += 1
            else:
                fallidos += 1
        except Exception as e:
            print(f"Error al procesar membresía {
                membresia.id}: {str(e)}")  # type: ignore
            fallidos += 1

    return exitosos, fallidos, total


def enviar_correo_membresias_por_vencer(dias_anticipacion=7):
    fecha_limite = timezone.now().date() + timezone.timedelta(days=dias_anticipacion)

    membresias_por_vencer = Membresia.objects.filter(
        estado='ACTIVA',
        fecha_fin__lte=fecha_limite,
        fecha_fin__gt=timezone.now().date(),
        socio__email__isnull=False
    ).select_related('socio', 'plan')

    exitosos = 0
    fallidos = 0
    total = membresias_por_vencer.count()

    for membresia in membresias_por_vencer:
        try:
            resultado = Membresia.enviar_email(membresia.id)  # type: ignore
            if resultado:
                exitosos += 1
            else:
                fallidos += 1
        except Exception as e:
            print(f"Error al procesar membresía {
                  membresia.id}: {str(e)}")  # type: ignore
            fallidos += 1

    return exitosos, fallidos, total


class email_vencidas(View):
    def get(self, request):
        exitosos, fallidos, total = enviar_correo_membresias_vencidas()
        return redirect('membresia_list')


class email_por_vencer(View):
    def get(self, request):
        exitosos, fallidos, total = enviar_correo_membresias_por_vencer()
        return redirect('membresia_list')
