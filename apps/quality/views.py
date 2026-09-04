from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from apps.common.generic import CrudCreateView, CrudDeleteView, CrudDetailView, CrudListView, CrudUpdateView

from .forms import InspectionForm
from .models import Inspection


class InspectionListView(CrudListView, ListView):
    model = Inspection
    title = 'Quality'
    app_label = 'quality'
    list_fields = ['order', 'aql', 'inspector', 'inspection_date', 'result']


class InspectionDetailView(CrudDetailView, DetailView):
    model = Inspection
    title = 'Quality'
    app_label = 'quality'


class InspectionCreateView(CrudCreateView, CreateView):
    model = Inspection
    form_class = InspectionForm
    title = 'Add Inspection'
    app_label = 'quality'


class InspectionUpdateView(CrudUpdateView, UpdateView):
    model = Inspection
    form_class = InspectionForm
    title = 'Edit Inspection'
    app_label = 'quality'


class InspectionDeleteView(CrudDeleteView, DeleteView):
    model = Inspection
    app_label = 'quality'
