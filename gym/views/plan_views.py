from dataclasses import fields
from django.db.models.base import Model as Model
from django.shortcuts import redirect
from django.urls import reverse_lazy
from gym.models import Plan
from gym.forms import PlanForm
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
from gym.filters import DynamicFilterSet, DynamicModelFilter
from django.shortcuts import render
from gym.views.general_views import AdvancedFilterListView
from django.views.generic import ListView
from django_filters.views import FilterView
from django import forms
import django_filters as filters
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, ButtonHolder, Submit
from django.db import models


from django.views.generic import ListView
from django.apps import apps
from django.http import Http404, HttpResponseBadRequest
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class DynamicFilterListView(ListView):
    template_name = 'plan/plan_filter.html'
    paginate_by = 20

    def get_model(self):
        app_label = self.kwargs.get('app_label')
        model_name = self.kwargs.get('model_name')
        try:
            return apps.get_model(app_label, model_name)
        except LookupError:
            raise Http404("Modelo no encontrado")

    def get_queryset(self):
        model = self.get_model()
        filterset = DynamicModelFilter(
            self.request.GET, queryset=model.objects.all())
        return filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.get_model()
        context['filter'] = DynamicModelFilter(
            self.request.GET, queryset=model.objects.all())
        context['model_name'] = model._meta.verbose_name_plural
        # Agregar los campos del modelo al contexto
        context['model_fields'] = model._meta.fields
        return context


class planFilterView(ListView):
    model = Plan
    fields = ['nombre', 'precio', 'duracion', 'descripcion']
    template_name = 'plan/plan_filter.html'
    context_object_name = 'objetos'
    paginate_by = 20  # Opcional: paginación

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = DynamicFilterSet(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context


class planListView(PermissionRequiredMixin, AdvancedFilterListView):
    model = Plan
    template_name = 'plan/plan_list.html'
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.view_plan'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Listado de Planes'
        kwargs['create_url'] = reverse_lazy('plan_create')
        kwargs['crumb_url'] = reverse_lazy('plan_list')
        kwargs['crumb_name'] = 'Planes'
        return super().get_context_data(**kwargs)


class planCreateView(PermissionRequiredMixin, CreateView):
    model = Plan
    form_class = PlanForm
    template_name = 'plan/plan_create.html'
    success_url = reverse_lazy('plan_list')
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.add_plan'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Crear Plan'
        kwargs['crumb_url'] = reverse_lazy('plan_list')
        kwargs['crumb_name'] = 'Planes'
        return super().get_context_data(**kwargs)


class planUpdateView(PermissionRequiredMixin, UpdateView):
    model = Plan
    form_class = PlanForm
    template_name = 'plan/plan_create.html'
    success_url = reverse_lazy('plan_list')
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.change_plan'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Editar Plan'
        kwargs['crumb_url'] = reverse_lazy('plan_list')
        kwargs['crumb_name'] = 'Planes'
        return super().get_context_data(**kwargs)


class planDeleteView(PermissionRequiredMixin, DeleteView):
    model = Plan
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('plan_list')
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.delete_plan'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['cancel_url'] = reverse_lazy('plan_list')
        return super().get_context_data(**kwargs)


class planDetailView(PermissionRequiredMixin, DetailView):
    model = Plan
    template_name = 'plan/plan_detail.html'
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.view_plan'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar estaacción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Detalle Plan'
        kwargs['crumb_url'] = reverse_lazy('plan_list')
        kwargs['crumb_name'] = 'Planes'
        kwargs['cancel_url'] = reverse_lazy('plan_list')
        return super().get_context_data(**kwargs)
