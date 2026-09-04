from django.db import models


class Factory(models.Model):
    TYPE_CHOICES = [("garment", "Garment Factory"), ("material_supplier", "Material Supplier")]

    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150, blank=True)
    factory_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Factories"

    def __str__(self):
        return self.name


class FactoryCapability(models.Model):
    factory = models.ForeignKey(Factory, related_name="capabilities", on_delete=models.CASCADE)
    product_category = models.CharField(max_length=100)
    monthly_capacity = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.factory.name} — {self.product_category}"


class FactoryCompliance(models.Model):
    factory = models.ForeignKey(Factory, related_name="compliances", on_delete=models.CASCADE)
    certification_name = models.CharField(max_length=100)
    certificate_number = models.CharField(max_length=100, blank=True)
    valid_until = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Factory compliances"

    def __str__(self):
        return f"{self.factory.name} — {self.certification_name}"


class FactoryCommercialTerm(models.Model):
    factory = models.OneToOneField(Factory, related_name="commercial_terms", on_delete=models.CASCADE)
    payment_terms = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=5, default="USD")
    moq = models.PositiveIntegerField(null=True, blank=True)
    lead_time_days = models.PositiveIntegerField(null=True, blank=True)
    price_terms = models.CharField(max_length=50, blank=True)
    shipment_terms = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Commercial terms — {self.factory.name}"
