from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, DeleteView

from .forms import DocumentUploadForm
from .models import Document


class DocumentUploadView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentUploadForm
    template_name = 'crud/form.html'

    def dispatch(self, request, *args, **kwargs):
        self.ct = get_object_or_404(ContentType, pk=kwargs['content_type_id'])
        self.object_id = kwargs['object_id']
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.content_type = self.ct
        form.instance.object_id = self.object_id
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Upload Document'
        return ctx

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', reverse('dashboard:home'))


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Document
    template_name = 'crud/confirm_delete.html'

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', reverse('dashboard:home'))
