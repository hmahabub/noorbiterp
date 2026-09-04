from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from apps.approvals.models import ApprovalRequest
from apps.common.generic import CrudCreateView, CrudDeleteView, CrudDetailView, CrudListView, CrudUpdateView
from apps.users.models import User

from .forms import SamplePOForm
from .models import SamplePO


class SampleListView(CrudListView, ListView):
    model = SamplePO
    title = 'Samples'
    app_label = 'samples'
    list_fields = ['po_number', 'buyer', 'factory', 'sample_type', 'status', 'md_approved']


class SampleDetailView(CrudDetailView, DetailView):
    model = SamplePO
    title = 'Samples'
    app_label = 'samples'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['items'] = self.object.items.all()
        return ctx


class SampleCreateView(CrudCreateView, CreateView):
    model = SamplePO
    form_class = SamplePOForm
    title = 'Add Sample PO'
    app_label = 'samples'

    def form_valid(self, form):
        response = super().form_valid(form)
        # Every new SamplePO auto-creates an ApprovalRequest routed to any MD user
        md_user = User.objects.filter(is_md=True).first()
        if md_user:
            from django.contrib.contenttypes.models import ContentType
            ApprovalRequest.objects.create(
                content_type=ContentType.objects.get_for_model(SamplePO),
                object_id=self.object.pk,
                requested_by=self.request.user,
                approver=md_user,
            )
            messages.info(self.request, 'MD approval has been requested for this Sample PO.')
        return response


class SampleUpdateView(CrudUpdateView, UpdateView):
    model = SamplePO
    form_class = SamplePOForm
    title = 'Edit Sample PO'
    app_label = 'samples'


class SampleDeleteView(CrudDeleteView, DeleteView):
    model = SamplePO
    app_label = 'samples'
