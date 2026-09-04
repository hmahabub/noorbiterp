from django.contrib import admin

from .models import SamplePO, SampleItem


class SampleItemInline(admin.TabularInline):
    model = SampleItem
    extra = 1


@admin.register(SamplePO)
class SamplePOAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'buyer', 'factory', 'sample_type', 'status', 'md_approved', 'requested_date')
    list_filter = ('sample_type', 'status', 'md_approved', 'fabric_source')
    search_fields = ('po_number', 'p_number')
    inlines = [SampleItemInline]
