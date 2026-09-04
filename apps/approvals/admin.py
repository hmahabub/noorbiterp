from django.contrib import admin

from .models import ApprovalRequest, AuditLog


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_type', 'object_id', 'requested_by', 'approver', 'status', 'requested_at')
    list_filter = ('status', 'content_type')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_type', 'object_id', 'action', 'timestamp')
    list_filter = ('action', 'content_type')
    readonly_fields = [f.name for f in AuditLog._meta.fields]
