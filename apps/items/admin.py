from django.contrib import admin

from .models import FinishedItem, FinishedItemVariant, Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('supplier_code', 'description', 'type', 'size', 'color', 'unit_price', 'unit', 'supplier')
    list_filter = ('type', 'unit', 'supplier')
    search_fields = ('supplier_code', 'description')


class FinishedItemVariantInline(admin.TabularInline):
    model = FinishedItemVariant
    extra = 1
    readonly_fields = ('sku',)


@admin.register(FinishedItem)
class FinishedItemAdmin(admin.ModelAdmin):
    list_display = ('buyer_style', 'description', 'type', 'finish', 'unit_price')
    list_filter = ('type',)
    search_fields = ('buyer_style', 'description')
    inlines = [FinishedItemVariantInline]


@admin.register(FinishedItemVariant)
class FinishedItemVariantAdmin(admin.ModelAdmin):
    list_display = ('sku', 'finished_item', 'color_name', 'size', 'status', 'is_active')
    list_filter = ('status', 'is_active', 'size')
    search_fields = ('sku', 'color_name', 'finished_item__buyer_style')
    readonly_fields = ('sku',)
