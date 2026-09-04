from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from apps.common.generic import CrudCreateView, CrudDeleteView, CrudDetailView, CrudListView, CrudUpdateView

from .forms import SupplierPOForm
from .models import SupplierPO


class SupplierPOListView(CrudListView, ListView):
    model = SupplierPO
    title = 'Procurement'
    app_label = 'procurement'
    list_fields = ['po_number', 'order', 'supplier', 'material_type', 'status']


class SupplierPODetailView(CrudDetailView, DetailView):
    model = SupplierPO
    title = 'Procurement'
    app_label = 'procurement'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['items'] = self.object.items.all()
        return ctx


class SupplierPOCreateView(CrudCreateView, CreateView):
    model = SupplierPO
    form_class = SupplierPOForm
    title = 'Add Supplier PO'
    app_label = 'procurement'


class SupplierPOUpdateView(CrudUpdateView, UpdateView):
    model = SupplierPO
    form_class = SupplierPOForm
    title = 'Edit Supplier PO'
    app_label = 'procurement'


class SupplierPODeleteView(CrudDeleteView, DeleteView):
    model = SupplierPO
    app_label = 'procurement'
