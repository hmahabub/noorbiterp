from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from apps.common.generic import CrudCreateView, CrudDeleteView, CrudDetailView, CrudListView, CrudUpdateView

from .forms import FactoryForm
from .models import Factory


class FactoryListView(CrudListView, ListView):
    model = Factory
    title = 'Factories'
    app_label = 'factories'
    list_fields = ['name', 'factory_type', 'location', 'is_active']


class FactoryDetailView(CrudDetailView, DetailView):
    model = Factory
    title = 'Factories'
    app_label = 'factories'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['capabilities'] = self.object.capabilities.all()
        ctx['compliances'] = self.object.compliances.all()
        return ctx


class FactoryCreateView(CrudCreateView, CreateView):
    model = Factory
    form_class = FactoryForm
    title = 'Add Factory'
    app_label = 'factories'


class FactoryUpdateView(CrudUpdateView, UpdateView):
    model = Factory
    form_class = FactoryForm
    title = 'Edit Factory'
    app_label = 'factories'


class FactoryDeleteView(CrudDeleteView, DeleteView):
    model = Factory
    app_label = 'factories'
