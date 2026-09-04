from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('doc_type', 'content_type', 'object_id', 'uploaded_by', 'uploaded_at')
    list_filter = ('doc_type', 'content_type')
    search_fields = ('remarks',)
