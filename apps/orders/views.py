from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from apps.common.generic import CrudCreateView, CrudDeleteView, CrudListView, CrudUpdateView

from .forms import OrderForm, OrderItemBreakdownForm, OrderItemForm, OrderItemHeaderEditForm
from .models import Order, OrderItem, OrderItemBreakdown


class OrderListView(CrudListView, ListView):
    model = Order
    title = 'Orders'
    app_label = 'orders'
    list_fields = ['our_order_number', 'buyer_order_number', 'buyer', 'status', 'required_ship_date']


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['order_items'] = self.object.items.select_related('item').prefetch_related('breakdown__variant')
        ctx['total_amount'] = self.object.total_amount
        ctx['total_qty'] = self.object.total_qty
        ctx['documents'] = self._documents()
        ctx['content_type_id'] = ContentType.objects.get_for_model(Order).pk
        return ctx

    def _documents(self):
        from apps.documents.models import Document
        ct = ContentType.objects.get_for_model(Order)
        return Document.objects.filter(content_type=ct, object_id=self.object.pk)


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'crud/form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'New Order'
        ctx['url_names'] = {'list': 'orders:list'}
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Order {self.object.our_order_number} created. Now add items.')
        return response

    def get_success_url(self):
        return reverse('orders:add_item', args=[self.object.pk])


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'crud/form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = f'Edit {self.object.our_order_number}'
        ctx['url_names'] = {'list': 'orders:list'}
        return ctx

    def get_success_url(self):
        return reverse('orders:detail', args=[self.object.pk])


class OrderDeleteView(LoginRequiredMixin, DeleteView):
    model = Order
    template_name = 'crud/confirm_delete.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['url_names'] = {'list': 'orders:list'}
        return ctx

    def get_success_url(self):
        return reverse('orders:list')


# ---------------------------------------------------------------------------
# Step 2 + 3 combined: "Add items to Order" — add a style (OrderItem), which
# auto-provisions a qty=0 row for every active color/size variant; those
# render as an editable size-curve grid (colors x sizes) right below, the
# same single-screen pattern used for Purchase Orders.
# ---------------------------------------------------------------------------
class AddOrderItemView(LoginRequiredMixin, CreateView):
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'orders/add_item.html'

    def dispatch(self, request, *args, **kwargs):
        self.order = get_object_or_404(Order, pk=kwargs['order_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['order'] = self.order
        order_items = list(self.order.items.select_related('item'))
        for oi in order_items:
            oi.ensure_variant_rows()  # picks up any variants added since this page was last loaded
            oi.matrix = oi.breakdown_matrix()
            oi.edit_form = OrderItemHeaderEditForm(instance=oi, prefix=f'edit{oi.pk}')
        ctx['order_items'] = order_items
        ctx['total_amount'] = self.order.total_amount
        return ctx

    def post(self, request, *args, **kwargs):
        # Three different forms can post to this same URL: the "add style"
        # form at the top, each order item's inline "edit header" form, and
        # each order item's size-curve grid.
        action = request.POST.get('action')
        if action == 'save_grid':
            return self._handle_save_grid(request)
        if action == 'edit_item':
            return self._handle_edit_item(request)
        return super().post(request, *args, **kwargs)

    def _handle_edit_item(self, request):
        order_item = get_object_or_404(OrderItem, pk=request.POST.get('order_item_id'), order=self.order)
        form = OrderItemHeaderEditForm(request.POST, instance=order_item, prefix=f'edit{order_item.pk}')
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated {order_item.item.buyer_style} — pack {order_item.pack}, qty {order_item.qty}.')
        else:
            error_text = "; ".join(f"{f}: {', '.join(e)}" for f, e in form.errors.items())
            messages.error(request, f'Could not update that line — {error_text}')
        return redirect('orders:add_item', order_pk=self.order.pk)

    def _handle_save_grid(self, request):
        order_item = get_object_or_404(OrderItem, pk=request.POST.get('order_item_id'), order=self.order)
        updated = 0
        for line in order_item.breakdown.all():
            field_name = f'qty_{line.pk}'
            if field_name not in request.POST:
                continue
            try:
                new_qty = max(int(request.POST.get(field_name) or 0), 0)
            except ValueError:
                continue
            if new_qty != line.qty:
                line.qty = new_qty
                line.save(update_fields=['qty'])
                updated += 1
        if updated:
            messages.success(request, f'Saved {updated} quantity change(s) for {order_item.item.buyer_style}.')
        else:
            messages.info(request, 'No quantity changes to save.')
        return redirect('orders:add_item', order_pk=self.order.pk)

    def form_valid(self, form):
        form.instance.order = self.order
        if not form.instance.unit_price:
            form.instance.unit_price = form.instance.item.unit_price
        response = super().form_valid(form)
        self.object.ensure_variant_rows()
        messages.success(self.request, f'Added {form.instance.item.buyer_style} to {self.order.our_order_number}. Fill in quantities below.')
        return response

    def get_success_url(self):
        return reverse('orders:add_item', args=[self.order.pk])


@login_required
def remove_order_item(request, order_pk, pk):
    order = get_object_or_404(Order, pk=order_pk)
    line = get_object_or_404(OrderItem, pk=pk, order=order)
    line.delete()
    messages.success(request, 'Item removed from the order.')
    return redirect('orders:add_item', order_pk=order.pk)


@login_required
def remove_order_item_variant_inline(request, order_pk, pk):
    """Remove a breakdown row from the combined add-item page."""
    order = get_object_or_404(Order, pk=order_pk)
    line = get_object_or_404(OrderItemBreakdown, pk=pk, order_item__order=order)
    line.delete()
    messages.success(request, 'Variant line removed.')
    return redirect('orders:add_item', order_pk=order.pk)


# ---------------------------------------------------------------------------
# Standalone per-item variant page — still available for direct linking
# (e.g. revisiting a single style's breakdown later), though the combined
# add-item page above is now the primary workflow.
# ---------------------------------------------------------------------------
class AddOrderItemVariantView(LoginRequiredMixin, CreateView):
    model = OrderItemBreakdown
    form_class = OrderItemBreakdownForm
    template_name = 'orders/add_variant.html'

    def dispatch(self, request, *args, **kwargs):
        self.order_item = get_object_or_404(OrderItem, pk=kwargs['order_item_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['order_item'] = self.order_item
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial['unit_price'] = self.order_item.unit_price
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['order_item'] = self.order_item
        ctx['breakdown'] = self.order_item.breakdown.select_related('variant')
        return ctx

    def form_valid(self, form):
        form.instance.order_item = self.order_item
        if not form.instance.unit_price:
            form.instance.unit_price = self.order_item.unit_price
        messages.success(
            self.request,
            f'Added {form.instance.variant.color_name} / {form.instance.variant.size} — qty {form.instance.qty}.'
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('orders:add_variant', args=[self.order_item.pk])


@login_required
def remove_order_item_variant(request, order_item_pk, pk):
    order_item = get_object_or_404(OrderItem, pk=order_item_pk)
    line = get_object_or_404(OrderItemBreakdown, pk=pk, order_item=order_item)
    line.delete()
    messages.success(request, 'Variant line removed.')
    return redirect('orders:add_variant', order_item_pk=order_item.pk)