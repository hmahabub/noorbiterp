
from decimal import Decimal

from django.db import models
from django.utils import timezone


class Order(models.Model):
    ORDER_TYPE = [("sample", "Sample"), ("bulk", "Bulk")]
    STATUS = [("inquiry", "Inquiry"), ("costing", "Costing"), ("negotiation", "Price Negotiation"),
              ("confirmed", "Confirmed"), ("booking", "Booking"), ("in_production", "In Production"),
              ("shipped", "Shipped"), ("completed", "Completed"), ("cancelled", "Cancelled")]

    buyer_order_number = models.CharField(max_length=30, blank=True, help_text="Buyer's own PO number, e.g. WC6824")

    buyer = models.ForeignKey("buyers.Buyer", on_delete=models.PROTECT, related_name="orders")
    ship_to = models.ForeignKey(
        "buyers.BuyerShipTo", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="orders", verbose_name="Ship To",
    )
    factory = models.ForeignKey(
        "factories.Factory", on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )

    order_type = models.CharField(max_length=10, choices=ORDER_TYPE, default="bulk")
    status = models.CharField(max_length=20, choices=STATUS, default="inquiry")
    currency = models.CharField(max_length=5, default="USD")

    booking_date = models.DateField(null=True, blank=True)
    confirmed_date = models.DateField(null=True, blank=True)
    required_ship_date = models.DateField(null=True, blank=True)
    planned_ship_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    terms_and_conditions = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.our_order_number or f"Order (unsaved) #{self.pk}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.our_order_number:
            # Needs the primary key first: ORD-<year>-<id>, e.g. ORD-2026-00042
            self.our_order_number = f"ORD-{timezone.now().year}-{self.pk:05d}"
            super().save(update_fields=["our_order_number"])

    @property
    def our_order_number(self):
        return f"ORD-{self.created_at.year}-{self.pk:05d}"

    @property
    def shipment_status_color(self):
        if self.status in ("shipped", "completed"):
            return "green"
        if not self.required_ship_date:
            return "green"
        today = timezone.now().date()
        if today > self.required_ship_date:
            return "red"
        if (self.required_ship_date - today).days <= 7:  # configurable N-day window
            return "yellow"
        return "green"

    @property
    def total_amount(self):
        return self.items.aggregate(
            total=models.Sum(models.F("qty") * models.F("unit_price"))
        )["total"] or Decimal("0")

    @property
    def total_qty(self):
        return self.items.aggregate(total=models.Sum("qty"))["total"] or 0

    @property
    def total_bom_cost(self):
        """Sum of every order line's material cost — an order-level rollup
        of the order-wise BOM & costing."""
        return sum((oi.total_bom_cost for oi in self.items.all()), Decimal("0"))

    @property
    def estimated_margin(self):
        return self.total_amount - self.total_bom_cost


class OrderItem(models.Model):
    """One style/line on the order — mirrors Section 1 of the buyer's PO
    sheet (Style No. / Body Description / Q'ty / FOB / Extension)."""

    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    item = models.ForeignKey("items.FinishedItem", on_delete=models.PROTECT, related_name="order_lines")
    qty = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=4)
    pack = models.CharField(max_length=5, default="A", help_text="Pack code, e.g. A/B/C")

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.item.buyer_style} x {self.qty}"

    @property
    def line_total(self):
        return (self.qty or 0) * (self.unit_price or 0)

    @property
    def breakdown_qty(self):
        return self.breakdown.aggregate(total=models.Sum("qty"))["total"] or 0

    @property
    def breakdown_balanced(self):
        """True once the color/size breakdown quantities add up to the
        style-level qty — mirrors the buyer sheet's own Section 1 vs
        Section 2 total cross-check."""
        return self.breakdown_qty == self.qty

    @property
    def nonzero_breakdown(self):
        """Breakdown rows with a real quantity — used on the read-only order
        detail page so zero-qty placeholder rows don't clutter the summary."""
        return self.breakdown.filter(qty__gt=0).select_related("variant")

    def ensure_variant_rows(self):
        """Auto-provisions a qty=0 OrderItemBreakdown row for every active
        color/size variant of this style, so the size-curve grid always has
        a cell to edit without a separate 'add variant' step. Idempotent —
        safe to call on every page load, including after new variants are
        added to the Finished Item later."""
        existing_variant_ids = set(self.breakdown.values_list("variant_id", flat=True))
        missing = self.item.variants.filter(is_active=True).exclude(pk__in=existing_variant_ids)
        OrderItemBreakdown.objects.bulk_create([
            OrderItemBreakdown(order_item=self, variant=variant, qty=0, unit_price=self.unit_price)
            for variant in missing
        ])

    def ensure_bom_lines(self):
        """Clones any standard BOM lines (from the Finished Item) that
        aren't already on this order line yet, so the order-wise BOM always
        starts from the style's standard recipe. Idempotent and additive —
        already-cloned/edited lines are left untouched, and any new standard
        materials added later get picked up on the next visit."""
        from apps.costing.models import OrderItemBOMLine

        existing_item_ids = set(self.bom_lines.values_list("item_id", flat=True))
        missing = self.item.bom_lines.exclude(item_id__in=existing_item_ids)
        OrderItemBOMLine.objects.bulk_create([
            OrderItemBOMLine(
                order_item=self, category=std.category, item=std.item,
                consumption=std.consumption, unit=std.unit,
                wastage_percent=std.wastage_percent, unit_price=std.unit_price,
            )
            for std in missing
        ])

    @property
    def total_bom_cost(self):
        from decimal import Decimal
        return sum((line.line_cost for line in self.bom_lines.all()), Decimal("0"))

    @property
    def estimated_margin(self):
        return self.line_total - self.total_bom_cost

    def breakdown_matrix(self):
        """Builds the color (rows) x size (columns) grid: {'sizes': [...],
        'rows': [{'color': ..., 'cells': [{'size', 'variant', 'breakdown'}]}]}"""
        from apps.items.models import FinishedItemVariant

        size_order = [code for code, _ in FinishedItemVariant.SIZE_CHOICES]
        variants = list(self.item.variants.filter(is_active=True))
        sizes_present = sorted({v.size for v in variants}, key=lambda s: size_order.index(s) if s in size_order else 999)

        colors_present = []
        seen = set()
        for v in sorted(variants, key=lambda v: v.color_name):
            if v.color_name not in seen:
                seen.add(v.color_name)
                colors_present.append(v.color_name)

        breakdown_map = {(b.variant.color_name, b.variant.size): b for b in self.breakdown.select_related("variant")}
        variant_map = {(v.color_name, v.size): v for v in variants}

        rows = []
        for color in colors_present:
            cells = []
            for size in sizes_present:
                variant = variant_map.get((color, size))
                cells.append({
                    "size": size,
                    "variant": variant,
                    "breakdown": breakdown_map.get((color, size)) if variant else None,
                })
            rows.append({"color": color, "cells": cells})

        return {"sizes": sizes_present, "rows": rows}

    def save(self, *args, **kwargs):
        if self.unit_price is None:
            self.unit_price = self.item.unit_price
        super().save(*args, **kwargs)


class OrderItemBreakdown(models.Model):
    """A single color/size/qty row under an OrderItem — mirrors Section 2 of
    the buyer's PO sheet (Color & Size Breakdown)."""

    order_item = models.ForeignKey(OrderItem, related_name="breakdown", on_delete=models.CASCADE)
    variant = models.ForeignKey("items.FinishedItemVariant", on_delete=models.PROTECT, related_name="order_breakdown_lines")
    qty = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        ordering = ["id"]
        verbose_name = "Order Item Breakdown"
        verbose_name_plural = "Order Item Breakdowns"

    def __str__(self):
        return f"{self.variant.sku} x {self.qty}"

    @property
    def line_total(self):
        return (self.qty or 0) * (self.unit_price or 0)

    def save(self, *args, **kwargs):
        if self.unit_price is None:
            self.unit_price = self.order_item.unit_price
        super().save(*args, **kwargs)