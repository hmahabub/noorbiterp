from django.db import models


def generate_shipment_id():
    last = Shipment.objects.order_by('-id').first()
    next_num = (last.id + 1) if last else 1
    from django.utils import timezone
    return f"SH-{timezone.now().year}-{next_num:05d}"


class Shipment(models.Model):
    MODE = [("sea", "Sea"), ("air", "Air"), ("courier", "Courier"), ("road", "Road"), ("other", "Other")]
    STATUS = [("split", "Split"), ("half", "Half"), ("full", "Full"), ("partial", "Partial")]

    shipment_id = models.CharField(max_length=30, unique=True, editable=False)
    order = models.ForeignKey("orders.Order", related_name="shipments", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    required_ship_date = models.DateField(editable=False, null=True, blank=True)
    planned_ship_date = models.DateField()
    mode = models.CharField(max_length=10, choices=MODE)
    status = models.CharField(max_length=10, choices=STATUS)
    vessel = models.CharField(max_length=100, blank=True)
    container = models.CharField(max_length=100, blank=True)
    etd = models.DateField(null=True, blank=True)
    eta = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-planned_ship_date']

    def save(self, *args, **kwargs):
        if not self.shipment_id:
            self.shipment_id = generate_shipment_id()
        self.required_ship_date = self.order.required_ship_date
        super().save(*args, **kwargs)

    def __str__(self):
        return self.shipment_id

    @property
    def buyer(self):
        return self.order.buyer

    @property
    def factory(self):
        return self.order.factory


class ShipmentFollowUp(models.Model):
    RISK = [("low", "Low"), ("medium", "Medium"), ("high", "High")]

    shipment = models.ForeignKey(Shipment, related_name="followups", on_delete=models.CASCADE)
    followup_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=100, blank=True)
    quantity_on_time = models.PositiveIntegerField(default=0)
    quantity_outstanding = models.PositiveIntegerField(default=0)
    document_status = models.CharField(max_length=20, default="pending")  # drives red-light indicator
    booking_date = models.DateField(null=True, blank=True)
    risk = models.CharField(max_length=10, choices=RISK, default="low")
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-followup_date']

    def __str__(self):
        return f"{self.shipment.shipment_id} follow-up ({self.followup_date})"
