from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.users.models import User


class Document(models.Model):
    DOC_TYPE_CHOICES = [
        ("buyer_agreement", "Buyer Agreement"), ("compliance_manual", "Compliance Manual"),
        ("quality_manual", "Quality Manual"), ("packaging_guideline", "Packaging Guideline"),
        ("rsl", "RSL"), ("brand_guideline", "Brand Guideline"),
        ("po", "PO"), ("pi", "PI"), ("lc", "LC"), ("bl", "Bill of Lading"),
        ("awb", "Air Waybill"), ("commercial_invoice", "Commercial Invoice"),
        ("packing_list", "Packing List"), ("certificate_of_origin", "Certificate of Origin"),
        ("inspection_certificate", "Inspection Certificate"), ("test_report", "Test Report"),
        ("other", "Other"),
    ]

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    linked_object = GenericForeignKey("content_type", "object_id")

    doc_type = models.CharField(max_length=40, choices=DOC_TYPE_CHOICES)
    file = models.FileField(upload_to="documents/%Y/%m/")
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.get_doc_type_display()} ({self.file.name.split('/')[-1]})"
