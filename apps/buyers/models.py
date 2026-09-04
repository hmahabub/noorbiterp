from django.core.cache import cache
from django.db import models


class Buyer(models.Model):
    BUYER_TYPE = [("local", "Local"), ("international", "International")]
    CATEGORY = [("brand", "Brand"), ("wholesaler", "Wholesaler"), ("retailer", "Retailer")]

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    country = models.CharField(max_length=80)
    city = models.CharField(max_length=80, blank=True)
    website = models.URLField(blank=True)
    brand = models.CharField(max_length=100, blank=True)
    buyer_type = models.CharField(max_length=15, choices=BUYER_TYPE)
    category = models.CharField(max_length=15, choices=CATEGORY)
    is_active = models.BooleanField(default=True)  # green/red status
    currency = models.CharField(max_length=5, default="USD")
    payment_terms = models.CharField(max_length=100, blank=True)
    credit_limit = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    incoterms = models.CharField(max_length=20, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    default_factory = models.ForeignKey(
        "factories.Factory", null=True, blank=True, on_delete=models.SET_NULL, related_name="default_for_buyers"
    )
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.code} — {self.name}"

    @property
    def performance(self):
        """Aggregated buyer performance, cached 15 min so it never drifts from source data
        while avoiding recomputation on every page hit (see plan section 4.1)."""
        cache_key = f"buyer_performance_{self.pk}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        from apps.orders.models import Order
        orders = Order.objects.filter(buyer=self)
        data = {
            'total_orders': orders.count(),
            'running_orders': orders.exclude(status__in=['completed', 'cancelled']).count(),
            'completed_orders': orders.filter(status='completed').count(),
            'cancelled_orders': orders.filter(status='cancelled').count(),
        }
        cache.set(cache_key, data, 60 * 15)
        return data


class BuyerContact(models.Model):
    buyer = models.ForeignKey(Buyer, related_name="contacts", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=80, blank=True)
    department = models.CharField(max_length=80, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    wechat = models.CharField(max_length=30, blank=True)
    kakao = models.CharField(max_length=30, blank=True)
    preferred_channel = models.CharField(max_length=20, blank=True)
    alternate_contact = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Buyer contacts"

    def __str__(self):
        return f"{self.name} ({self.buyer.name})"

class BuyerShipTo(models.Model):
    """A buyer can have several ship-to destinations (warehouses, DCs); an
    Order picks one of these. Kept separate from BuyerContact since it's an
    address, not a person."""
    buyer = models.ForeignKey(Buyer, related_name="ship_to_addresses", on_delete=models.CASCADE)
    label = models.CharField(max_length=100)  # e.g. "Main Warehouse - Bell, CA"
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_default", "label"]
        verbose_name = "Ship-to address"
        verbose_name_plural = "Ship-to addresses"

    def __str__(self):
        return f"{self.buyer.name} — {self.label}"

    @property
    def full_address(self):
        parts = [self.address_line1, self.address_line2, self.city, self.state, self.postal_code, self.country]
        return ", ".join(p for p in parts if p)
        
class BuyerRequirement(models.Model):
    buyer = models.OneToOneField(Buyer, related_name="requirement", on_delete=models.CASCADE)
    product_category = models.CharField(max_length=100, blank=True)  # kids/men's/boys'/ladies'
    packaging_requirement = models.TextField(blank=True)
    label_requirement = models.TextField(blank=True)
    poly_requirement = models.TextField(blank=True)
    fabric_preference = models.TextField(blank=True)
    special_requirement = models.TextField(blank=True)
    aql = models.CharField(max_length=20, blank=True)
    inspection_requirement = models.TextField(blank=True)
    sample_requirement = models.CharField(max_length=100, blank=True)  # Proto/Fit/PP

    def __str__(self):
        return f"Requirements — {self.buyer.name}"
