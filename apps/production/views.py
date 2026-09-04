from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from apps.common.generic import CrudCreateView, CrudDeleteView, CrudDetailView, CrudListView, CrudUpdateView

from .forms import ProductionUpdateForm
from .models import ProductionUpdate


class ProductionListView(CrudListView, ListView):
    model = ProductionUpdate
    title = 'Production'
    app_label = 'production'
    list_fields = ['order', 'stage', 'update_date', 'quantity_completed', 'ready_quantity']


class ProductionDetailView(CrudDetailView, DetailView):
    model = ProductionUpdate
    title = 'Production'
    app_label = 'production'


class ProductionCreateView(CrudCreateView, CreateView):
    model = ProductionUpdate
    form_class = ProductionUpdateForm
    title = 'Add Production Update'
    app_label = 'production'

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class ProductionUpdateEditView(CrudUpdateView, UpdateView):
    model = ProductionUpdate
    form_class = ProductionUpdateForm
    title = 'Edit Production Update'
    app_label = 'production'


class ProductionDeleteView(CrudDeleteView, DeleteView):
    model = ProductionUpdate
    app_label = 'production'
