from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .services import get_dashboard_kpis


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(get_dashboard_kpis(self.request.user))
        return ctx
