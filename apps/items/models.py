from django.db import models


class Item(models.Model):
    TYPE_CHOICES = [
        ("fabric", "Fabric"),
        ("trims", "Trims"),
        ("accessories", "Accessories"),
        ("packaging", "Packaging"),
        ("label", "Label"),
        ("other", "Other"),
    ]

    UNIT_CHOICES = [
        ("pcs", "Pcs"), ("yds", "Yards"), ("mtr", "Meter"), ("kg", "Kg"),
        ("gm", "Gram"), ("set", "Set"), ("dozen", "Dozen"), ("roll", "Roll"),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    supplier_code = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=255)
    size = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=4)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="pcs")
    supplier = models.ForeignKey(
        "factories.Factory", on_delete=models.PROTECT, related_name="items"
    )

    class Meta:
        ordering = ["description"]

    def __str__(self):
        label = self.supplier_code or self.description
        return f"{label} — {self.get_type_display()}"


class FinishedItem(models.Model):
    """A buyer-facing finished-garment style — what goes on an Order, as
    opposed to `Item` above which is a raw material/trim used on Purchase
    Orders. e.g. buyer_style 'WS806G318' — 'POLY CARGO SHORT (SEAN)'."""

    TYPE_CHOICES = [
        ("shorts", "Shorts"), ("pants", "Pants"), ("shirt", "Shirt"),
        ("t_shirt", "T-Shirt"), ("polo", "Polo"), ("jacket", "Jacket"),
        ("dress", "Dress"), ("skirt", "Skirt"), ("sweater", "Sweater"),
        ("outerwear", "Outerwear"), ("other", "Other"),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    buyer_style = models.CharField(max_length=50, help_text="Buyer's style number, e.g. WS806G318")
    description = models.CharField(max_length=255)
    content = models.TextField(blank=True, verbose_name="Content", help_text="Fabric content / construction, e.g. 100% Polyester T400 75D...")
    finish = models.CharField(max_length=50, blank=True, verbose_name="Finish", help_text="Wash/finish code, e.g. NW, GW")
    unit_price = models.DecimalField(max_digits=10, decimal_places=4, help_text="Reference FOB unit price")

    class Meta:
        ordering = ["buyer_style"]
        verbose_name = "Finished Item"

    def __str__(self):
        return f"{self.buyer_style} — {self.description}"

    @property
    def standard_bom_cost(self):
        """Total standard material cost to make 1 unit — sum of every
        StandardBOMLine's line_cost. Compare against `unit_price` (the FOB
        price) to see the implied margin before CM/overhead."""
        from decimal import Decimal
        return sum((line.line_cost for line in self.bom_lines.all()), Decimal("0"))


class FinishedItemVariant(models.Model):
    """A specific color/size of a FinishedItem — what actually gets ordered
    with a quantity on an OrderItemBreakdown line."""

    SIZE_CHOICES = [
        ("XS", "XS"), ("S", "S"), ("M", "M"), ("L", "L"), ("XL", "XL"),
        ("XXL", "XXL"), ("XXXL", "XXXL"),
    ]
    STATUS_CHOICES = [
        ("draft", "Draft"), ("active", "Active"), ("discontinued", "Discontinued"),
    ]

    finished_item = models.ForeignKey(FinishedItem, related_name="variants", on_delete=models.CASCADE)
    color_name = models.CharField(max_length=50)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    sku = models.CharField(max_length=100, unique=True, editable=False, blank=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="active")

    class Meta:
        ordering = ["finished_item", "color_name", "size"]
        verbose_name = "Finished Item Variant"
        unique_together = [("finished_item", "color_name", "size")]

    def __str__(self):
        return f"{self.sku or self.finished_item.buyer_style} / {self.color_name} / {self.size}"

    def save(self, *args, **kwargs):
        if not self.sku:
            color_slug = "".join(ch for ch in self.color_name.upper() if ch.isalnum() or ch == " ").strip().replace(" ", "-")
            self.sku = f"{self.finished_item.buyer_style}-{color_slug}-{self.size}"
        super().save(*args, **kwargs)