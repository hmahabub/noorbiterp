from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from apps.common.generic import CrudCreateView, CrudDeleteView, CrudDetailView, CrudListView, CrudUpdateView

from .forms import FinishedItemForm, FinishedItemVariantForm, ItemForm
from .models import FinishedItem, FinishedItemVariant, Item


# ---------------------------------------------------------------------------
# Item (raw materials / trims — used on Purchase Orders)
# ---------------------------------------------------------------------------
class ItemListView(CrudListView, ListView):
    model = Item
    title = 'Items'
    app_label = 'items'
    list_fields = ['supplier_code', 'description', 'type', 'unit_price', 'unit', 'supplier']

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(description__icontains=q)
        return qs


class ItemDetailView(CrudDetailView, DetailView):
    model = Item
    title = 'Items'
    app_label = 'items'


class ItemCreateView(CrudCreateView, CreateView):
    model = Item
    form_class = ItemForm
    title = 'Add Item'
    app_label = 'items'


class ItemUpdateView(CrudUpdateView, UpdateView):
    model = Item
    form_class = ItemForm
    title = 'Edit Item'
    app_label = 'items'


class ItemDeleteView(CrudDeleteView, DeleteView):
    model = Item
    app_label = 'items'


# ---------------------------------------------------------------------------
# FinishedItem (buyer-facing styles — used on Orders) + variants (color/size)
# ---------------------------------------------------------------------------
class FinishedItemListView(CrudListView, ListView):
    model = FinishedItem
    title = 'Finished Items'
    app_label = 'finished_items'
    list_fields = ['buyer_style', 'description', 'type', 'finish', 'unit_price']

    def get_url_names(self):
        return {
            'list': 'items:finished_list', 'detail': 'items:finished_detail',
            'create': 'items:finished_create', 'update': 'items:finished_update',
            'delete': 'items:finished_delete',
        }

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(buyer_style__icontains=q)
        return qs


class FinishedItemDetailView(LoginRequiredMixin, DetailView):
    model = FinishedItem
    template_name = 'items/finished_item_detail.html'
    context_object_name = 'finished_item'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['variants'] = self.object.variants.all()
        return ctx


class FinishedItemCreateView(CrudCreateView, CreateView):
    model = FinishedItem
    form_class = FinishedItemForm
    title = 'Add Finished Item'
    app_label = 'finished_items'

    def get_url_names(self):
        return FinishedItemListView.get_url_names(self)

    def get_success_url(self):
        # Straight into variant management — mirrors the PO "create -> add
        # items" flow: a finished item is only useful once it has variants.
        return reverse('items:finished_add_variant', args=[self.object.pk])


class FinishedItemUpdateView(CrudUpdateView, UpdateView):
    model = FinishedItem
    form_class = FinishedItemForm
    title = 'Edit Finished Item'
    app_label = 'finished_items'

    def get_url_names(self):
        return FinishedItemListView.get_url_names(self)

    def get_success_url(self):
        return reverse('items:finished_detail', args=[self.object.pk])


class FinishedItemDeleteView(CrudDeleteView, DeleteView):
    model = FinishedItem
    app_label = 'finished_items'

    def get_url_names(self):
        return FinishedItemListView.get_url_names(self)


class AddFinishedItemVariantView(LoginRequiredMixin, CreateView):
    model = FinishedItemVariant
    form_class = FinishedItemVariantForm
    template_name = 'items/add_variant.html'

    def dispatch(self, request, *args, **kwargs):
        self.finished_item = get_object_or_404(FinishedItem, pk=kwargs['finished_item_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['finished_item'] = self.finished_item
        ctx['variants'] = self.finished_item.variants.all()
        return ctx

    def form_valid(self, form):
        form.instance.finished_item = self.finished_item
        messages.success(
            self.request,
            f'Added {form.instance.color_name} / {form.instance.size} to {self.finished_item.buyer_style}.'
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('items:finished_add_variant', args=[self.finished_item.pk])


@login_required
def remove_finished_item_variant(request, finished_item_pk, pk):
    finished_item = get_object_or_404(FinishedItem, pk=finished_item_pk)
    variant = get_object_or_404(FinishedItemVariant, pk=pk, finished_item=finished_item)
    variant.delete()
    messages.success(request, 'Variant removed.')
    return redirect('items:finished_add_variant', finished_item_pk=finished_item.pk)
