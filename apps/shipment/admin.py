from django.contrib import admin

from .models import Shipment, ShipmentFollowUp


class ShipmentFollowUpInline(admin.TabularInline):
    model = ShipmentFollowUp
    extra = 0


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('shipment_id', 'order', 'quantity', 'mode', 'status', 'planned_ship_date', 'eta')
    list_filter = ('mode', 'status')
    readonly_fields = ('shipment_id', 'required_ship_date')
    inlines = [ShipmentFollowUpInline]
