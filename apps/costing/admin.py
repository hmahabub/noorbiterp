from django.contrib import admin

from .models import CostingLine, CostingSheet


class CostingLineInline(admin.TabularInline):
    model = CostingLine
    extra = 1


@admin.register(CostingSheet)
class CostingSheetAdmin(admin.ModelAdmin):
    list_display = ('order_item', 'version', 'total_cost', 'currency', 'status', 'approved_by')
    list_filter = ('status', 'currency')
    inlines = [CostingLineInline]


@admin.register(CostingLine)
class CostingLineAdmin(admin.ModelAdmin):
    list_display = ('costing_sheet', 'category', 'component_name', 'unit_price', 'consumption', 'wastage_percent', 'cost')
    list_filter = ('category',)
    search_fields = ('component_name', 'description', 'supplier_info')
