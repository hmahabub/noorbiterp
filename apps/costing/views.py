from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from apps.common.generic import CrudCreateView, CrudDeleteView, CrudDetailView, CrudListView, CrudUpdateView
from apps.items.models import FinishedItem
from apps.orders.models import OrderItem

from .forms import CostingSheetForm, OrderItemBOMLineForm, StandardBOMLineForm
from .models import CostingSheet, OrderItemBOMLine, StandardBOMLine


class CostingListView(CrudListView, ListView):
    model = CostingSheet
    title = 'Costing & BOM'
    app_label = 'costing'
    list_fields = ['order', 'version', 'total_cost', 'currency', 'status']


class CostingDetailView(CrudDetailView, DetailView):
    model = CostingSheet
    title = 'Costing & BOM'
    app_label = 'costing'


class CostingCreateView(CrudCreateView, CreateView):
    model = CostingSheet
    form_class = CostingSheetForm
    title = 'Add Costing Sheet'
    app_label = 'costing'


class CostingUpdateView(CrudUpdateView, UpdateView):
    model = CostingSheet
    form_class = CostingSheetForm
    title = 'Edit Costing Sheet'
    app_label = 'costing'


class CostingDeleteView(CrudDeleteView, DeleteView):
    model = CostingSheet
    app_label = 'costing'


# ---------------------------------------------------------------------------
# Standard BOM & Costing — one page per Finished Item: add a material,
# it appears below in the table with inline edit (details/summary), and a
# running "Standard Cost per Unit" footer compared against the style's
# reference FOB price. This is THE standard recipe cloned onto every order.
# ---------------------------------------------------------------------------
class FinishedItemBOMView(LoginRequiredMixin, CreateView):
    model = StandardBOMLine
    form_class = StandardBOMLineForm
    template_name = 'costing/standard_bom.html'

    def dispatch(self, request, *args, **kwargs):
        self.finished_item = get_object_or_404(FinishedItem, pk=kwargs['finished_item_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['finished_item'] = self.finished_item
        lines = list(self.finished_item.bom_lines.select_related('item'))
        for line in lines:
            line.edit_form = StandardBOMLineForm(instance=line, prefix=f'edit{line.pk}')
        ctx['bom_lines'] = lines
        ctx['standard_cost'] = self.finished_item.standard_bom_cost
        ctx['reference_price'] = self.finished_item.unit_price
        ctx['implied_margin'] = self.finished_item.unit_price - self.finished_item.standard_bom_cost
        return ctx

    def post(self, request, *args, **kwargs):
        if request.POST.get('action') == 'edit_line':
            return self._handle_edit_line(request)
        return super().post(request, *args, **kwargs)

    def _handle_edit_line(self, request):
        line = get_object_or_404(StandardBOMLine, pk=request.POST.get('line_id'), finished_item=self.finished_item)
        form = StandardBOMLineForm(request.POST, instance=line, prefix=f'edit{line.pk}')
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated {line.item.description}.')
        else:
            error_text = "; ".join(f"{f}: {', '.join(e)}" for f, e in form.errors.items())
            messages.error(request, f'Could not update that line — {error_text}')
        return redirect('costing:standard_bom', finished_item_pk=self.finished_item.pk)

    def form_valid(self, form):
        form.instance.finished_item = self.finished_item
        if not form.instance.unit_price:
            form.instance.unit_price = form.instance.item.unit_price
        messages.success(self.request, f'Added {form.instance.item.description} to the standard BOM.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('costing:standard_bom', args=[self.finished_item.pk])


@login_required
def delete_standard_bom_line(request, finished_item_pk, pk):
    finished_item = get_object_or_404(FinishedItem, pk=finished_item_pk)
    line = get_object_or_404(StandardBOMLine, pk=pk, finished_item=finished_item)
    line.delete()
    messages.success(request, 'Removed from the standard BOM.')
    return redirect('costing:standard_bom', finished_item_pk=finished_item.pk)


# ---------------------------------------------------------------------------
# Order-wise BOM & Costing — one page per order line (OrderItem). On first
# visit it clones the style's standard BOM, scaled by this line's qty, so
# there's a ready-to-review procurement quantity for every material.
# ---------------------------------------------------------------------------
class OrderItemBOMView(LoginRequiredMixin, CreateView):
    model = OrderItemBOMLine
    form_class = OrderItemBOMLineForm
    template_name = 'costing/order_item_bom.html'

    def dispatch(self, request, *args, **kwargs):
        self.order_item = get_object_or_404(OrderItem, pk=kwargs['order_item_pk'])
        self.order_item.ensure_bom_lines()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['order_item'] = self.order_item
        lines = list(self.order_item.bom_lines.select_related('item'))
        for line in lines:
            line.edit_form = OrderItemBOMLineForm(instance=line, prefix=f'edit{line.pk}')
        ctx['bom_lines'] = lines
        ctx['total_material_cost'] = self.order_item.total_bom_cost
        ctx['revenue'] = self.order_item.line_total
        ctx['estimated_margin'] = self.order_item.estimated_margin
        return ctx

    def post(self, request, *args, **kwargs):
        if request.POST.get('action') == 'edit_line':
            return self._handle_edit_line(request)
        return super().post(request, *args, **kwargs)

    def _handle_edit_line(self, request):
        line = get_object_or_404(OrderItemBOMLine, pk=request.POST.get('line_id'), order_item=self.order_item)
        form = OrderItemBOMLineForm(request.POST, instance=line, prefix=f'edit{line.pk}')
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated {line.item.description}.')
        else:
            error_text = "; ".join(f"{f}: {', '.join(e)}" for f, e in form.errors.items())
            messages.error(request, f'Could not update that line — {error_text}')
        return redirect('costing:order_item_bom', order_item_pk=self.order_item.pk)

    def form_valid(self, form):
        form.instance.order_item = self.order_item
        if not form.instance.unit_price:
            form.instance.unit_price = form.instance.item.unit_price
        messages.success(self.request, f'Added {form.instance.item.description} to this line\'s BOM.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('costing:order_item_bom', args=[self.order_item.pk])


@login_required
def delete_order_item_bom_line(request, order_item_pk, pk):
    order_item = get_object_or_404(OrderItem, pk=order_item_pk)
    line = get_object_or_404(OrderItemBOMLine, pk=pk, order_item=order_item)
    line.delete()
    messages.success(request, "Removed from this order line's BOM.")
    return redirect('costing:order_item_bom', order_item_pk=order_item.pk)
