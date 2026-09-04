from django.db import models


class SupplierPO(models.Model):
    MATERIAL_TYPE = [("fabric", "Fabric"), ("trims", "Trims"), ("accessories", "Accessories")]
    STATUS = [("booked", "Booked"), ("partial", "Partially Received"), ("received", "Fully Received")]

    po_number = models.CharField(max_length=30, unique=True)
    order = models.ForeignKey("orders.Order", related_name="supplier_pos", on_delete=models.CASCADE)
    supplier = models.ForeignKey("factories.Factory", on_delete=models.PROTECT, related_name="supplier_pos")
    material_type = models.CharField(max_length=15, choices=MATERIAL_TYPE)
    booking_date = models.DateField()
    expected_receiving_date = models.DateField(null=True, blank=True)
    actual_receiving_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default="booked")

    class Meta:
        ordering = ['-booking_date']
        verbose_name = "Supplier PO"

    def __str__(self):
        return self.po_number


class MaterialItem(models.Model):
    supplier_po = models.ForeignKey(SupplierPO, related_name="items", on_delete=models.CASCADE)
    material_name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    unit = models.CharField(max_length=20)
    unit_price = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    def __str__(self):
        return f"{self.material_name} ({self.quantity} {self.unit})"
