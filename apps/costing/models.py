from django.db import models

from apps.items.models import Item


class CostingSheet(models.Model):
    STATUS = [("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved")]

    order = models.ForeignKey("orders.Order", related_name="costing_versions", on_delete=models.CASCADE)
    version = models.PositiveIntegerField(default=1)
    fabric_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    trims_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    cm_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    washing_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    freight_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=4, editable=False, default=0)
    currency = models.CharField(max_length=5, default="USD")
    status = models.CharField(max_length=10, choices=STATUS, default="draft")
    approved_by = models.ForeignKey("users.User", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.our_order_number} v{self.version}"

    def save(self, *args, **kwargs):
        self.total_cost = (
            self.fabric_cost + self.trims_cost + self.cm_cost + self.washing_cost + self.freight_cost
        )
        super().save(*args, **kwargs)


class StandardBOMLine(models.Model):
    """The standard Bill of Materials for a Finished Item — one row per raw
    material required to make ONE unit of the style. This is the reusable
    'recipe' (set as the standard for that style) that gets cloned, and
    scaled by order qty, onto every order line for that style."""

    finished_item = models.ForeignKey(
        "items.FinishedItem", related_name="bom_lines", on_delete=models.CASCADE
    )
    category = models.CharField(max_length=20, choices=Item.TYPE_CHOICES)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="standard_bom_lines")
    consumption = models.DecimalField(
        max_digits=10, decimal_places=4,
        help_text="Quantity of this material needed to make 1 finished unit"
    )
    unit = models.CharField(max_length=10, choices=Item.UNIT_CHOICES, default="pcs")
    wastage_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Wastage / buffer %, e.g. 5 for 5%"
    )
    unit_price = models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        ordering = ["category", "item__description"]
        verbose_name = "Standard BOM Line"

    def __str__(self):
        return f"{self.finished_item.buyer_style} — {self.item.description}"

    @property
    def total_qty(self):
        """Per-unit requirement including wastage — the standard
        per-garment consumption figure."""
        return (self.consumption or 0) * (1 + (self.wastage_percent or 0) / 100)

    @property
    def line_cost(self):
        return self.total_qty * (self.unit_price or 0)

    def save(self, *args, **kwargs):
        if self.unit_price is None:
            self.unit_price = self.item.unit_price
        super().save(*args, **kwargs)


class OrderItemBOMLine(models.Model):
    """The order-line-specific BOM — cloned from the Finished Item's
    standard BOM. Total Qty here is scaled by the order line's qty, so it's
    the actual procurement quantity needed for that order (not just the
    per-unit figure), while staying independently editable per order."""

    order_item = models.ForeignKey(
        "orders.OrderItem", related_name="bom_lines", on_delete=models.CASCADE
    )
    category = models.CharField(max_length=20, choices=Item.TYPE_CHOICES)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="order_bom_lines")
    consumption = models.DecimalField(
        max_digits=10, decimal_places=4,
        help_text="Quantity of this material needed to make 1 finished unit"
    )
    unit = models.CharField(max_length=10, choices=Item.UNIT_CHOICES, default="pcs")
    wastage_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        ordering = ["category", "item__description"]
        verbose_name = "Order BOM Line"

    def __str__(self):
        return f"{self.order_item} — {self.item.description}"

    @property
    def per_unit_qty(self):
        return (self.consumption or 0) * (1 + (self.wastage_percent or 0) / 100)

    @property
    def total_qty(self):
        """Total procurement quantity needed for the whole order line."""
        return self.per_unit_qty * (self.order_item.qty or 0)

    @property
    def line_cost(self):
        return self.total_qty * (self.unit_price or 0)

    def save(self, *args, **kwargs):
        if self.unit_price is None:
            self.unit_price = self.item.unit_price
        super().save(*args, **kwargs)