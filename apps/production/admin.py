from django.contrib import admin

from .models import ProductionUpdate, ShipmentSplit


@admin.register(ProductionUpdate)
class ProductionUpdateAdmin(admin.ModelAdmin):
    list_display = ('order', 'stage', 'update_date', 'quantity_completed', 'ready_quantity', 'updated_by')
    list_filter = ('stage',)


@admin.register(ShipmentSplit)
class ShipmentSplitAdmin(admin.ModelAdmin):
    list_display = ('order', 'split_sequence', 'planned_date', 'quantity')
