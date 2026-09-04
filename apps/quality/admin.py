from django.contrib import admin

from .models import Inspection, Claim


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ('order', 'aql', 'inspector', 'inspection_date', 'result')
    list_filter = ('result',)


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('order', 'claim_type', 'amount', 'status', 'date')
    list_filter = ('status',)
