from django.contrib import admin

from .models import CostingSheet, OrderItemBOMLine, StandardBOMLine


@admin.register(CostingSheet)
class CostingSheetAdmin(admin.ModelAdmin):
    list_display = ('order', 'version', 'total_cost', 'currency', 'status', 'approved_by')
    list_filter = ('status', 'currency')


class StandardBOMLineInline(admin.TabularInline):
    model = StandardBOMLine
    extra = 1


@admin.register(StandardBOMLine)
class StandardBOMLineAdmin(admin.ModelAdmin):
    list_display = ('finished_item', 'category', 'item', 'consumption', 'unit', 'wastage_percent', 'unit_price')
    list_filter = ('category', 'unit')
    search_fields = ('finished_item__buyer_style', 'item__description')


@admin.register(OrderItemBOMLine)
class OrderItemBOMLineAdmin(admin.ModelAdmin):
    list_display = ('order_item', 'category', 'item', 'consumption', 'unit', 'wastage_percent', 'unit_price')
    list_filter = ('category', 'unit')
    search_fields = ('order_item__item__buyer_style', 'item__description')
