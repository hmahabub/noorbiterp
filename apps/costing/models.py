from decimal import Decimal

from django.db import models


class CostingSheet(models.Model):
    """One cost sheet per order line (style) — the single place BOM
    (materials/consumption) and Costing (cost buildup to FOB) live together,
    matching a real buying-house cost sheet: components grouped by category,
    each with its own consumption/wastage/cost, rolling up to a FOB total."""

    STATUS = [("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved")]

    order_item = models.ForeignKey(
        "orders.OrderItem", related_name="costing_sheets", on_delete=models.CASCADE
    )
    version = models.PositiveIntegerField(default=1)
    currency = models.CharField(max_length=5, default="USD")
    status = models.CharField(max_length=10, choices=STATUS, default="draft")
    approved_by = models.ForeignKey("users.User", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-version"]
        unique_together = [("order_item", "version")]

    def __str__(self):
        return f"{self.order_item} — Costing v{self.version}"

    @property
    def total_cost(self):
        """Sum of every line's cost — this is the FOB price per unit once
        Fabric/Trims/.../CM/Washing/Test Cost/Commercial/Profit are all in."""
        return self.lines.aggregate(total=models.Sum("cost"))["total"] or Decimal("0")

    def subtotal_for(self, category):
        return self.lines.filter(category=category).aggregate(
            total=models.Sum("cost")
        )["total"] or Decimal("0")

    @property
    def category_subtotals(self):
        return [
            {"code": code, "label": label, "amount": self.subtotal_for(code)}
            for code, label in CostingLine.CATEGORY_CHOICES
        ]


class CostingLine(models.Model):
    """One row on the cost sheet — a material (Fabric/Trims/Labels &
    Packing/Embellishment) priced by unit_price x consumption x (1+wastage),
    or a flat cost entry (CM/Washing/Test Cost/Commercial Charges/Profit
    Margin) where `cost` is simply typed in directly. `cost` is always a
    plain editable field — the UI suggests a computed value via JS when
    unit_price/consumption are filled in, but never forces it, matching how
    the source spreadsheet mixes formulas and manual overrides."""

    CATEGORY_CHOICES = [
        ("fabric", "Fabric"),
        ("trims", "Trims"),
        ("labels_packing", "Labels & Packing"),
        ("embellishment", "Embellishment"),
        ("cm", "CM"),
        ("washing", "Washing"),
        ("test_cost", "Test Cost"),
        ("commercial_charges", "Commercial Charges"),
        ("profit_margin", "Profit Margin"),
    ]

    costing_sheet = models.ForeignKey(CostingSheet, related_name="lines", on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    component_name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    supplier_info = models.CharField(max_length=150, blank=True, verbose_name="Supplier Information")
    unit_price = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    consumption = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    wastage_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=4, default=0, verbose_name="Cost in US$")

    class Meta:
        ordering = ["category", "id"]
        verbose_name = "Costing Line"

    def __str__(self):
        return f"{self.get_category_display()} — {self.component_name}"

    def save(self, *args, **kwargs):
        if self.wastage_percent is None:
            self.wastage_percent = Decimal("0")
        if self.cost is None:
            self.cost = Decimal("0")
        super().save(*args, **kwargs)

    @property
    def part_of_price(self):
        """% this line contributes to the sheet's FOB total."""
        total = self.costing_sheet.total_cost
        if not total:
            return Decimal("0")
        return (self.cost / total) * 100
