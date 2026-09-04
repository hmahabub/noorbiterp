from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from apps.common.generic import CrudCreateView, CrudDeleteView, CrudListView, CrudUpdateView

from .forms import BuyerForm, BuyerShipToForm
from .models import Buyer, BuyerShipTo


class BuyerListView(CrudListView, ListView):
    model = Buyer
    title = 'Buyers'
    app_label = 'buyers'
    list_fields = ['code', 'name', 'country', 'buyer_type', 'category', 'is_active']

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(name__icontains=q)
        return qs


class BuyerDetailView(LoginRequiredMixin, DetailView):
    model = Buyer
    template_name = 'buyers/detail.html'
    context_object_name = 'buyer'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['performance'] = self.object.performance
        ctx['contacts'] = self.object.contacts.all()
        ctx['ship_to_addresses'] = self.object.ship_to_addresses.all()
        ctx['documents'] = self._documents()
        ctx['content_type_id'] = ContentType.objects.get_for_model(Buyer).pk
        return ctx

    def _documents(self):
        from apps.documents.models import Document
        ct = ContentType.objects.get_for_model(Buyer)
        return Document.objects.filter(content_type=ct, object_id=self.object.pk)


class BuyerCreateView(CrudCreateView, CreateView):
    model = Buyer
    form_class = BuyerForm
    title = 'Add Buyer'
    app_label = 'buyers'

    def get_success_url(self):
        return reverse('buyers:add_ship_to', args=[self.object.pk])

class BuyerUpdateView(CrudUpdateView, UpdateView):
    model = Buyer
    form_class = BuyerForm
    title = 'Edit Buyer'
    app_label = 'buyers'

    def get_success_url(self):
        return reverse('buyers:add_ship_to', args=[self.object.pk])

class BuyerDeleteView(CrudDeleteView, DeleteView):
    model = Buyer
    app_label = 'buyers'
    allow_delete = False

# ---------------------------------------------------------------------------
# Ship-to addresses — managed from the buyer detail page so order creation
# always has somewhere to route the order to.
# ---------------------------------------------------------------------------
class AddBuyerShipToView(LoginRequiredMixin, CreateView):
    model = BuyerShipTo
    form_class = BuyerShipToForm
    template_name = 'crud/form.html'

    def dispatch(self, request, *args, **kwargs):
        self.buyer = get_object_or_404(Buyer, pk=kwargs['buyer_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = f'Add Ship-To Address — {self.buyer.name}'
        return ctx

    def form_valid(self, form):
        form.instance.buyer = self.buyer
        messages.success(self.request, f'Added ship-to address "{form.instance.label}".')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('buyers:detail', args=[self.buyer.pk])


@login_required
def remove_ship_to(request, buyer_pk, pk):
    buyer = get_object_or_404(Buyer, pk=buyer_pk)
    ship_to = get_object_or_404(BuyerShipTo, pk=pk, buyer=buyer)
    ship_to.delete()
    messages.success(request, 'Ship-to address removed.')
    return redirect('buyers:detail', pk=buyer.pk)
