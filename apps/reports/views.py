from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from .services import REPORT_REGISTRY, generate_report


class ReportListView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['reports'] = REPORT_REGISTRY
        return ctx


class ReportDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        slug = kwargs['slug']
        report = next((r for r in REPORT_REGISTRY if r['slug'] == slug), None)
        ctx['report'] = report or {'slug': slug, 'name': slug.replace('-', ' ').title()}
        ctx.update(generate_report(slug))
        return ctx
