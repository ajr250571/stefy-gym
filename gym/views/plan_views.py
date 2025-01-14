from django.db.models.base import Model as Model
from django.shortcuts import redirect
from django.urls import reverse_lazy
from gym.models import Plan
from gym.forms import PlanForm
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class planListView(PermissionRequiredMixin, ListView):
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

    def get_queryset(self):
        return Plan.objects.all().order_by('nombre')


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
