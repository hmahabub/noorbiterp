from decimal import Decimal

MATERIAL_CATEGORIES = {"fabric", "trims", "labels_packing", "embellishment"}
CHARGE_CATEGORIES = {"cm", "washing", "test_cost", "commercial_charges", "profit_margin"}

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from apps.common.generic import CrudCreateView, CrudDeleteView, CrudDetailView, CrudListView, CrudUpdateView
from apps.orders.models import OrderItem

from .forms import CostingLineForm, CostingSheetForm
from .models import CostingLine, CostingSheet


class CostingListView(CrudListView, ListView):
    model = CostingSheet
    title = 'Costing Sheets'
    app_label = 'costing'
    list_fields = ['order_item', 'version', 'total_cost', 'currency', 'status']

    def get_url_names(self):
        names = super().get_url_names()
        names['detail'] = 'costing:sheet'  # the rich sheet page, not the generic CRUD detail
        return names


class CostingDetailView(CrudDetailView, DetailView):
    model = CostingSheet
    title = 'Costing Sheets'
    app_label = 'costing'


class CostingCreateView(CrudCreateView, CreateView):
    model = CostingSheet
    form_class = CostingSheetForm
    title = 'Add Costing Sheet'
    app_label = 'costing'

    def get_success_url(self):
        return reverse('costing:sheet', args=[self.object.pk])


class CostingUpdateView(CrudUpdateView, UpdateView):
    model = CostingSheet
    form_class = CostingSheetForm
    title = 'Edit Costing Sheet'
    app_label = 'costing'

    def get_success_url(self):
        return reverse('costing:sheet', args=[self.object.pk])


class CostingDeleteView(CrudDeleteView, DeleteView):
    model = CostingSheet
    app_label = 'costing'


# ---------------------------------------------------------------------------
# The unified BOM + Costing interface — one page per costing sheet. Add a
# component, it lands in its category group below with inline edit
# (details/summary) and delete; category subtotals and a grand FOB total
# roll up live, matching a real buying-house cost sheet in one screen.
# ---------------------------------------------------------------------------
@login_required
def open_order_item_costing(request, order_item_pk):
    """Entry point linked from the order pages — jumps to the latest costing
    sheet for this order line, creating version 1 the first time."""
    order_item = get_object_or_404(OrderItem, pk=order_item_pk)
    sheet = order_item.latest_costing_sheet
    if not sheet:
        sheet = CostingSheet.objects.create(order_item=order_item, version=1)
    return redirect('costing:sheet', pk=sheet.pk)


class CostingSheetView(LoginRequiredMixin, CreateView):
    model = CostingLine
    form_class = CostingLineForm
    template_name = 'costing/sheet.html'

    def dispatch(self, request, *args, **kwargs):
        self.sheet = get_object_or_404(CostingSheet, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        order_item = self.sheet.order_item
        order = order_item.order
        lines = list(self.sheet.lines.all())
        for line in lines:
            line.edit_form = CostingLineForm(instance=line, prefix=f'edit{line.pk}')

        ctx['sheet'] = self.sheet
        ctx['order_item'] = order_item
        ctx['order'] = order
        ctx['finished_item'] = order_item.item
        all_groups = self._group_by_category(lines)
        ctx['material_groups'] = [g for g in all_groups if g['code'] in MATERIAL_CATEGORIES]
        ctx['charge_groups'] = [g for g in all_groups if g['code'] in CHARGE_CATEGORIES]
        ctx['total_cost'] = self.sheet.total_cost
        ctx['total_for_order_qty'] = self.sheet.total_cost * (order_item.qty or 0)
        ctx['revenue'] = order_item.line_total
        ctx['margin_per_unit'] = order_item.unit_price - self.sheet.total_cost
        ctx['margin_percent'] = (
            (ctx['margin_per_unit'] / order_item.unit_price * 100)
            if order_item.unit_price else Decimal("0")
        )
        ctx['other_versions'] = order_item.costing_sheets.exclude(pk=self.sheet.pk)
        ctx['category_summary'] = self.sheet.category_subtotals
        return ctx

    @staticmethod
    def _group_by_category(lines):
        groups = []
        for code, label in CostingLine.CATEGORY_CHOICES:
            cat_lines = [line for line in lines if line.category == code]
            groups.append({
                "code": code,
                "label": label,
                "lines": cat_lines,
                "subtotal": sum((line.cost for line in cat_lines), Decimal("0")),
            })
        return groups

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        if action == 'edit_line':
            return self._handle_edit_line(request)
        if action == 'new_version':
            return self._handle_new_version(request)
        return super().post(request, *args, **kwargs)

    def _handle_edit_line(self, request):
        line = get_object_or_404(CostingLine, pk=request.POST.get('line_id'), costing_sheet=self.sheet)
        form = CostingLineForm(request.POST, instance=line, prefix=f'edit{line.pk}')
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated {line.component_name}.')
        else:
            error_text = "; ".join(f"{f}: {', '.join(e)}" for f, e in form.errors.items())
            messages.error(request, f'Could not update that line — {error_text}')
        return redirect('costing:sheet', pk=self.sheet.pk)

    def _handle_new_version(self, request):
        next_version = (
            self.sheet.order_item.costing_sheets.aggregate(m=Max('version'))['m'] or 0
        ) + 1
        new_sheet = CostingSheet.objects.create(
            order_item=self.sheet.order_item, version=next_version, currency=self.sheet.currency,
        )
        messages.success(request, f'Created costing sheet v{new_sheet.version}.')
        return redirect('costing:sheet', pk=new_sheet.pk)

    def form_valid(self, form):
        form.instance.costing_sheet = self.sheet
        messages.success(self.request, f'Added {form.instance.component_name}.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('costing:sheet', args=[self.sheet.pk])


@login_required
def delete_costing_line(request, pk):
    line = get_object_or_404(CostingLine, pk=pk)
    sheet_pk = line.costing_sheet_id
    line.delete()
    messages.success(request, 'Line removed.')
    return redirect('costing:sheet', pk=sheet_pk)


@login_required
def print_costing_sheet(request, pk):
    """Print-friendly HTML view of the cost sheet — the page has its own
    @media print styling and a "Print / Save as PDF" button that calls the
    browser's native window.print(), same approach used for Purchase Orders.
    No PDF library needed server-side."""
    sheet = get_object_or_404(CostingSheet, pk=pk)
    order_item = sheet.order_item
    lines = list(sheet.lines.all())
    context = {
        'sheet': sheet,
        'order_item': order_item,
        'order': order_item.order,
        'finished_item': order_item.item,
        'groups': CostingSheetView._group_by_category(lines),
        'total_cost': sheet.total_cost,
        'total_for_order_qty': sheet.total_cost * (order_item.qty or 0),
        'revenue': order_item.line_total,
        'margin_per_unit': order_item.unit_price - sheet.total_cost,
    }
    return render(request, 'costing/print.html', context)


@login_required
def download_costing_excel(request, pk):
    """Generates a formatted .xlsx snapshot of the cost sheet on the fly —
    grouped by category with subtotals and a FOB total, mirroring the sheet
    on screen."""
    import io

    from django.http import FileResponse
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    sheet = get_object_or_404(CostingSheet, pk=pk)
    order_item = sheet.order_item
    order = order_item.order
    finished_item = order_item.item

    wb = Workbook()
    ws = wb.active
    ws.title = f"Costing v{sheet.version}"[:31]

    NAVY = "10233F"
    AMBER = "E8A33D"
    LIGHT_GREY = "F4F6F9"
    BORDER_GREY = "D7DCE3"

    header_font = Font(name="Arial", bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill("solid", fgColor=NAVY)
    title_font = Font(name="Arial", bold=True, size=16, color=NAVY)
    label_font = Font(name="Arial", bold=True, size=9, color="6B7686")
    value_font = Font(name="Arial", size=10)
    total_font = Font(name="Arial", bold=True, size=11, color="FFFFFF")
    total_fill = PatternFill("solid", fgColor=NAVY)
    category_font = Font(name="Arial", bold=True, size=10, color="FFFFFF")
    category_fill = PatternFill("solid", fgColor="0F8B8D")
    thin_border = Border(*(Side(style="thin", color=BORDER_GREY),) * 4)
    money_fmt = '#,##0.0000'

    col_widths = [18, 22, 24, 14, 12, 10, 12, 10]
    for i, w in enumerate(col_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.merge_cells("A1:H1")
    ws["A1"] = f"COSTING SHEET — {finished_item.buyer_style} (v{sheet.version})"
    ws["A1"].font = title_font

    info_rows = [
        ("Style", finished_item.buyer_style, "Buyer", str(order.buyer)),
        ("Description", finished_item.description, "Buyer PO No.", order.buyer_order_number or "—"),
        ("Content", finished_item.content or "—", "Our Order No.", order.our_order_number),
        ("Finish", finished_item.finish or "—", "Factory", str(order.factory) if order.factory else "—"),
        ("Order Qty", order_item.qty, "Currency", sheet.currency),
        ("Pack", order_item.pack, "Status", sheet.get_status_display()),
    ]
    r = 3
    for left_label, left_val, right_label, right_val in info_rows:
        ws.cell(row=r, column=1, value=left_label).font = label_font
        ws.cell(row=r, column=2, value=str(left_val)).font = value_font
        ws.cell(row=r, column=4, value=right_label).font = label_font
        ws.cell(row=r, column=5, value=str(right_val)).font = value_font
        r += 1

    r += 1
    table_header_row = r
    headers = ["Component", "Description", "Supplier", "Unit Price", "Consumption", "Wastage %", "Cost", "% of FOB"]
    for c, h in enumerate(headers, start=1):
        cell = ws.cell(row=table_header_row, column=c, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = thin_border
        cell.alignment = Alignment(horizontal="center")
    r += 1

    total_cost = sheet.total_cost
    for code, label in CostingLine.CATEGORY_CHOICES:
        cat_lines = [line for line in sheet.lines.all() if line.category == code]
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
        cat_cell = ws.cell(row=r, column=1, value=label.upper())
        cat_cell.font = category_font
        for c in range(1, 9):
            ws.cell(row=r, column=c).fill = category_fill
        subtotal = sum((line.cost for line in cat_lines), 0)
        subtotal_cell = ws.cell(row=r, column=8, value=float(subtotal))
        subtotal_cell.font = category_font
        subtotal_cell.number_format = money_fmt
        r += 1

        if not cat_lines:
            ws.cell(row=r, column=1, value=f"No {label.lower()} lines.").font = Font(name="Arial", italic=True, size=9, color="9AA3B0")
            r += 1
            continue

        for line in cat_lines:
            values = [
                line.component_name, line.description or "—", line.supplier_info or "—",
                float(line.unit_price) if line.unit_price is not None else None,
                float(line.consumption) if line.consumption is not None else None,
                float(line.wastage_percent or 0),
                float(line.cost),
                float(line.part_of_price),
            ]
            for c, val in enumerate(values, start=1):
                cell = ws.cell(row=r, column=c, value=val)
                cell.font = value_font
                cell.border = thin_border
                if c in (4, 5, 6, 7, 8):
                    cell.alignment = Alignment(horizontal="right")
                    if c in (4, 7):
                        cell.number_format = money_fmt
                    elif c in (6, 8):
                        cell.number_format = '0.00"%"'
            r += 1

    r += 1
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
    fob_label_cell = ws.cell(row=r, column=1, value="FOB TOTAL")
    fob_label_cell.font = total_font
    fob_value_cell = ws.cell(row=r, column=7, value=float(total_cost))
    fob_value_cell.font = total_font
    fob_value_cell.number_format = money_fmt
    for c in range(1, 9):
        ws.cell(row=r, column=c).fill = total_fill

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    filename = f"Costing_{finished_item.buyer_style}_v{sheet.version}.xlsx"
    return FileResponse(
        buffer, as_attachment=True, filename=filename,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
