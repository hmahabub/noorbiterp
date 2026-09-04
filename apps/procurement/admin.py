from django.contrib import admin

from .models import SupplierPO, MaterialItem


class MaterialItemInline(admin.TabularInline):
    model = MaterialItem
    extra = 1


@admin.register(SupplierPO)
class SupplierPOAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'order', 'supplier', 'material_type', 'status', 'booking_date')
    list_filter = ('material_type', 'status')
    search_fields = ('po_number',)
    inlines = [MaterialItemInline]
