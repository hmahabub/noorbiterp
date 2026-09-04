from django.contrib import admin

from .models import PurchaseOrder, POItem


class POItemInline(admin.TabularInline):
    model = POItem
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = (
        'po_number', 'to_supplier', 'destination', 'style', 'payment_method',
        'status', 'delivery_date', 'created_by',
    )
    list_filter = ('status', 'payment_method')
    search_fields = ('po_number', 'customer_po_number', 'style')
    readonly_fields = ('po_number', 'created_at', 'submitted_at', 'approved_at')
    inlines = [POItemInline]
