from django.contrib import admin

from .models import Factory, FactoryCapability, FactoryCompliance, FactoryCommercialTerm


class FactoryCapabilityInline(admin.TabularInline):
    model = FactoryCapability
    extra = 1


class FactoryComplianceInline(admin.TabularInline):
    model = FactoryCompliance
    extra = 1


class FactoryCommercialTermInline(admin.StackedInline):
    model = FactoryCommercialTerm
    extra = 0
    max_num = 1


@admin.register(Factory)
class FactoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'factory_type', 'location', 'is_active')
    list_filter = ('factory_type', 'is_active')
    search_fields = ('name', 'location')
    inlines = [FactoryCapabilityInline, FactoryComplianceInline, FactoryCommercialTermInline]
