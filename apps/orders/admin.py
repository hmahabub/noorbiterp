from django.contrib import admin

from .models import Order, OrderItem, OrderItemBreakdown


class OrderItemBreakdownInline(admin.TabularInline):
    model = OrderItemBreakdown
    extra = 1


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    show_change_link = True


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('our_order_number', 'buyer_order_number', 'buyer', 'factory', 'status', 'required_ship_date')
    list_filter = ('status', 'order_type')
    search_fields = ('our_order_number', 'buyer_order_number')
    readonly_fields = ('our_order_number', 'created_at')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'item', 'pack', 'qty', 'unit_price', 'line_total')
    list_filter = ('pack',)
    inlines = [OrderItemBreakdownInline]
