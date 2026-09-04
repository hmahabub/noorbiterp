"""
Reusable CRUD view mixins used by every business app so we don't repeat
ListView/CreateView/UpdateView/DeleteView/DetailView boilerplate 11 times.

Every app's views.py subclasses these with a `model`, `form_fields`
(optional) and the handful of display fields it wants in the list table.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse, reverse_lazy
from django.core.exceptions import PermissionDenied

class CrudMeta:
    """Mixin providing the extra context every crud/*.html template expects."""

    title = None            # e.g. "Buyers"
    app_label = None        # e.g. "buyers"  -> used to build url names: buyers:list etc.
    list_fields = None      # list of model field names shown as table columns
    detail_fields = None    # list of model field names shown on the detail page
    icon = 'bi-folder'      # bootstrap-icons class, purely cosmetic

    def get_url_names(self):
        return {
            'list': f'{self.app_label}:list',
            'detail': f'{self.app_label}:detail',
            'create': f'{self.app_label}:create',
            'update': f'{self.app_label}:update',
            'delete': f'{self.app_label}:delete',
        }

    def _columns(self, field_names):
        columns = []
        for name in field_names:
            try:
                label = self.model._meta.get_field(name).verbose_name.title()
            except Exception:
                label = name.replace('_', ' ').title()
            columns.append({'name': name, 'label': label})
        return columns

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = self.title or self.model._meta.verbose_name_plural.title()
        ctx['app_label'] = self.app_label
        list_field_names = self.list_fields or [f.name for f in self.model._meta.fields][:6]
        detail_field_names = self.detail_fields or [f.name for f in self.model._meta.fields]
        ctx['list_columns'] = self._columns(list_field_names)
        ctx['detail_columns'] = self._columns(detail_field_names)
        ctx['url_names'] = self.get_url_names()
        if getattr(self, 'object', None) is not None:
            ctx['content_type_id'] = ContentType.objects.get_for_model(self.model).pk
        return ctx


class CrudListView(LoginRequiredMixin, CrudMeta):
    template_name = 'crud/list.html'
    paginate_by = 25


class CrudDetailView(LoginRequiredMixin, CrudMeta):
    template_name = 'crud/detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['documents'] = self._get_documents()
        return ctx

    def _get_documents(self):
        from apps.documents.models import Document
        ct = ContentType.objects.get_for_model(self.model)
        return Document.objects.filter(content_type=ct, object_id=self.object.pk)


class CrudCreateView(LoginRequiredMixin, CrudMeta):
    template_name = 'crud/form.html'

    def get_success_url(self):
        return reverse(self.get_url_names()['list'])


class CrudUpdateView(LoginRequiredMixin, CrudMeta):
    template_name = 'crud/form.html'

    def get_success_url(self):
        return reverse(self.get_url_names()['list'])


class CrudDeleteView(LoginRequiredMixin, CrudMeta):
    template_name = 'crud/confirm_delete.html'
    allow_delete = True
    
    def dispatch(self, request, *args, **kwargs):
        if not self.allow_delete:
            raise PermissionDenied("Delete operation is disabled for this module.")

        return super().dispatch(request, *args, **kwargs)
        
    def get_success_url(self):
        return reverse(self.get_url_names()['list'])
