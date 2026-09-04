from django.contrib import admin

from .models import FollowUpEntry


@admin.register(FollowUpEntry)
class FollowUpEntryAdmin(admin.ModelAdmin):
    list_display = ('order', 'followup_type', 'date', 'ready_quantity', 'updated_by')
    list_filter = ('followup_type',)
