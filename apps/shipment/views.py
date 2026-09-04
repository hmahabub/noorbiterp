from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from apps.common.generic import CrudCreateView, CrudDeleteView, CrudDetailView, CrudListView, CrudUpdateView

from .forms import ShipmentForm
from .models import Shipment


class ShipmentListView(CrudListView, ListView):
    model = Shipment
    title = 'Shipments'
    app_label = 'shipment'
    list_fields = ['shipment_id', 'order', 'mode', 'status', 'planned_ship_date', 'eta']


class ShipmentDetailView(CrudDetailView, DetailView):
    model = Shipment
    title = 'Shipments'
    app_label = 'shipment'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['followups'] = self.object.followups.all()
        return ctx


class ShipmentCreateView(CrudCreateView, CreateView):
    model = Shipment
    form_class = ShipmentForm
    title = 'Add Shipment'
    app_label = 'shipment'


class ShipmentUpdateView(CrudUpdateView, UpdateView):
    model = Shipment
    form_class = ShipmentForm
    title = 'Edit Shipment'
    app_label = 'shipment'


class ShipmentDeleteView(CrudDeleteView, DeleteView):
    model = Shipment
    app_label = 'shipment'
