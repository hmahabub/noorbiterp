from django.contrib import admin

from .models import Buyer, BuyerContact, BuyerRequirement, BuyerShipTo


class BuyerContactInline(admin.TabularInline):
    model = BuyerContact
    extra = 1


class BuyerShipToInline(admin.TabularInline):
    model = BuyerShipTo
    extra = 1


class BuyerRequirementInline(admin.StackedInline):
    model = BuyerRequirement
    extra = 0
    max_num = 1


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'country', 'buyer_type', 'category', 'is_active', 'currency')
    list_filter = ('buyer_type', 'category', 'is_active', 'country')
    search_fields = ('code', 'name', 'country', 'brand')
    inlines = [BuyerContactInline, BuyerShipToInline, BuyerRequirementInline]


@admin.register(BuyerShipTo)
class BuyerShipToAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'label', 'city', 'country', 'is_default')
    list_filter = ('is_default', 'country')
    search_fields = ('label', 'buyer__name')

