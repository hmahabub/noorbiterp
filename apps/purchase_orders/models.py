from decimal import Decimal

from django.db import models
from django.utils import timezone


class PurchaseOrder(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("fob", "FOB - Free On Board"),
        ("ex_works", "Ex Works"),
        ("cpt", "CPT - Carriage Paid To"),
        ("cif", "CIF - Cost, Insurance & Freight"),
        ("fca", "FCA - Free Carrier"),
        ("cfr", "CFR - Cost & Freight"),
        ("dap", "DAP - Delivered At Place"),
        ("ddp", "DDP - Delivered Duty Paid"),
    ]
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("pending_approval", "Pending Approval"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    po_number = models.CharField(max_length=30, unique=True, editable=False, blank=True)

    to_supplier = models.ForeignKey(
        "factories.Factory", on_delete=models.PROTECT,
        related_name="purchase_orders_to", verbose_name="To (Supplier)",
    )
    destination = models.ForeignKey(
        "factories.Factory", on_delete=models.PROTECT,
        related_name="purchase_orders_destination", verbose_name="Destination",
    )

    season = models.CharField(max_length=50, blank=True)
    style = models.CharField(max_length=100, blank=True)
    customer_po_number = models.CharField(max_length=50, blank=True)
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHOD_CHOICES)
    delivery_date = models.DateField(null=True, blank=True)
    shipping_method = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    terms_and_conditions = models.TextField(blank=True, default=
            "1. Quality should be as per buyer approval\n"
            "2. Color as per buyer approval")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_by = models.ForeignKey(
        "users.User", on_delete=models.PROTECT, related_name="purchase_orders_created"
    )
    approved_by = models.ForeignKey(
        "users.User", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="purchase_orders_approved",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Purchase Order"

    def __str__(self):
        return self.po_number or f"PO (unsaved) #{self.pk}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.po_number:
            # PO number needs the primary key, so it's assigned right after the
            # first insert: PO-<year>-<pk>, e.g. PO-2026-00042
            self.po_number = f"PO-{timezone.now().year}-{self.pk:05d}"
            super().save(update_fields=["po_number"])

    @property
    def total_amount(self):
        return self.line_items.aggregate(
            total=models.Sum(models.F("qty") * models.F("unit_price"))
        )["total"] or Decimal("0")

    @property
    def can_edit_items(self):
        return self.status == "draft"

    @property
    def can_submit(self):
        return self.status == "draft" and self.line_items.exists()


class POItem(models.Model):
    po = models.ForeignKey(PurchaseOrder, related_name="line_items", on_delete=models.CASCADE)
    item = models.ForeignKey("items.Item", on_delete=models.PROTECT, related_name="po_lines")
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.item.description} x {self.qty}"

    @property
    def line_total(self):
        return (self.qty or 0) * (self.unit_price or 0)

    def save(self, *args, **kwargs):
        if self.unit_price is None:
            self.unit_price = self.item.unit_price
        super().save(*args, **kwargs)
