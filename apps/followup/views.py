from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from apps.common.generic import CrudCreateView, CrudDeleteView, CrudDetailView, CrudListView, CrudUpdateView

from .forms import FollowUpEntryForm
from .models import FollowUpEntry


class FollowUpListView(CrudListView, ListView):
    model = FollowUpEntry
    title = 'Follow-up'
    app_label = 'followup'
    list_fields = ['order', 'followup_type', 'date', 'ready_quantity', 'updated_by']


class FollowUpDetailView(CrudDetailView, DetailView):
    model = FollowUpEntry
    title = 'Follow-up'
    app_label = 'followup'


class FollowUpCreateView(CrudCreateView, CreateView):
    model = FollowUpEntry
    form_class = FollowUpEntryForm
    title = 'Add Follow-up Entry'
    app_label = 'followup'

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class FollowUpUpdateView(CrudUpdateView, UpdateView):
    model = FollowUpEntry
    form_class = FollowUpEntryForm
    title = 'Edit Follow-up Entry'
    app_label = 'followup'


class FollowUpDeleteView(CrudDeleteView, DeleteView):
    model = FollowUpEntry
    app_label = 'followup'
