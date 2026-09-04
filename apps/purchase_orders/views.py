from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from apps.approvals.models import ApprovalRequest
from apps.common.generic import CrudCreateView, CrudDeleteView, CrudListView, CrudUpdateView
from apps.users.models import User

from .forms import POItemForm, PurchaseOrderForm
from .models import POItem, PurchaseOrder


class PurchaseOrderListView(CrudListView, ListView):
    model = PurchaseOrder
    title = 'Purchase Orders'
    app_label = 'purchase_orders'
    list_fields = ['po_number', 'to_supplier', 'destination', 'style', 'status', 'delivery_date']


class PurchaseOrderDetailView(LoginRequiredMixin, DetailView):
    model = PurchaseOrder
    template_name = 'purchase_orders/detail.html'
    context_object_name = 'po'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['line_items'] = self.object.line_items.select_related('item')
        ctx['total_amount'] = self.object.total_amount
        ctx['documents'] = self._documents()
        ctx['content_type_id'] = ContentType.objects.get_for_model(PurchaseOrder).pk
        return ctx

    def _documents(self):
        from apps.documents.models import Document
        ct = ContentType.objects.get_for_model(PurchaseOrder)
        return Document.objects.filter(content_type=ct, object_id=self.object.pk)


class PurchaseOrderCreateView(LoginRequiredMixin, CreateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'crud/form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'New Purchase Order'
        ctx['url_names'] = {'list': 'purchase_orders:list'}
        return ctx

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Purchase Order {self.object.po_number} created. Now add the items.'
        )
        return response

    def get_success_url(self):
        return reverse('purchase_orders:add_item', args=[self.object.pk])


class PurchaseOrderUpdateView(LoginRequiredMixin, UpdateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'crud/form.html'

    def dispatch(self, request, *args, **kwargs):
        po = self.get_object()
        if po.status != 'draft':
            messages.error(request, 'Only draft purchase orders can be edited.')
            return redirect('purchase_orders:detail', pk=po.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = f'Edit {self.object.po_number}'
        ctx['url_names'] = {'list': 'purchase_orders:list'}
        return ctx

    def get_success_url(self):
        return reverse('purchase_orders:detail', args=[self.object.pk])


class PurchaseOrderDeleteView(LoginRequiredMixin, DeleteView):
    model = PurchaseOrder
    template_name = 'crud/confirm_delete.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['url_names'] = {'list': 'purchase_orders:list'}
        return ctx

    def get_success_url(self):
        return reverse('purchase_orders:list')


# ---------------------------------------------------------------------------
# "Add item to PO" workflow page — shown right after creating a PO header,
# and reachable again any time while the PO is still a draft.
# ---------------------------------------------------------------------------
class AddPOItemView(LoginRequiredMixin, CreateView):
    model = POItem
    form_class = POItemForm
    template_name = 'purchase_orders/add_item.html'

    def dispatch(self, request, *args, **kwargs):
        self.po = get_object_or_404(PurchaseOrder, pk=kwargs['po_pk'])
        if not self.po.can_edit_items:
            messages.error(request, 'Items can only be added while the PO is still a draft.')
            return redirect('purchase_orders:detail', pk=self.po.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['po'] = self.po
        ctx['line_items'] = self.po.line_items.select_related('item')
        ctx['total_amount'] = self.po.total_amount
        return ctx

    def form_valid(self, form):
        form.instance.po = self.po
        if not form.instance.unit_price:
            form.instance.unit_price = form.instance.item.unit_price
        messages.success(self.request, f'Added {form.instance.item.description} to {self.po.po_number}.')
        return super().form_valid(form)

    def get_success_url(self):
        # Stay on the same page so the user can keep adding lines.
        return reverse('purchase_orders:add_item', args=[self.po.pk])


@login_required
def remove_po_item(request, po_pk, pk):
    po = get_object_or_404(PurchaseOrder, pk=po_pk)
    if not po.can_edit_items:
        messages.error(request, 'Items can only be removed while the PO is still a draft.')
        return redirect('purchase_orders:detail', pk=po.pk)
    line = get_object_or_404(POItem, pk=pk, po=po)
    line.delete()
    messages.success(request, 'Line item removed.')
    return redirect('purchase_orders:add_item', po_pk=po.pk)


@login_required
def submit_for_approval(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if not po.can_submit:
        messages.error(request, 'Add at least one item before submitting this PO for approval.')
        return redirect('purchase_orders:detail', pk=po.pk)

    md_user = User.objects.filter(is_md=True).first()
    if not md_user:
        messages.error(request, 'No MD user is configured to approve this PO. Contact an administrator.')
        return redirect('purchase_orders:detail', pk=po.pk)

    po.status = 'pending_approval'
    po.submitted_at = timezone.now()
    po.save(update_fields=['status', 'submitted_at'])

    ApprovalRequest.objects.create(
        content_type=ContentType.objects.get_for_model(PurchaseOrder),
        object_id=po.pk,
        requested_by=request.user,
        approver=md_user,
    )
    messages.success(request, f'{po.po_number} submitted for MD approval.')
    return redirect('purchase_orders:detail', pk=po.pk)


@login_required
def print_po(request, pk):
    """Print-friendly HTML view of the approved PO. The page has its own
    @media print styling and a "Print / Save as PDF" button that calls the
    browser's native window.print() — no PDF library needed server-side."""
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if po.status != 'approved':
        messages.error(request, 'The printable PO is available once this PO has been approved.')
        return redirect('purchase_orders:detail', pk=po.pk)
    context = {
        'po': po,
        'line_items': po.line_items.select_related('item'),
        'total_amount': po.total_amount,
    }
    return render(request, 'purchase_orders/print.html', context)
