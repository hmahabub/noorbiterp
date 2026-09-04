from django.db import models


class ProductionUpdate(models.Model):
    STAGE = [("cutting", "Cutting"), ("sewing", "Sewing"), ("finishing", "Finishing"), ("packing", "Packing")]

    order = models.ForeignKey("orders.Order", related_name="production_updates", on_delete=models.CASCADE)
    stage = models.CharField(max_length=15, choices=STAGE)
    update_date = models.DateField(auto_now_add=True)
    quantity_completed = models.PositiveIntegerField(default=0)
    lc_status = models.CharField(max_length=50, blank=True)
    condition = models.CharField(max_length=100, blank=True)
    ready_quantity = models.PositiveIntegerField(default=0)
    remarks = models.TextField(blank=True)
    updated_by = models.ForeignKey("users.User", on_delete=models.PROTECT)

    class Meta:
        ordering = ['-update_date']

    def __str__(self):
        return f"{self.order.order_number} — {self.get_stage_display()} ({self.update_date})"


class ShipmentSplit(models.Model):
    order = models.ForeignKey("orders.Order", related_name="shipment_splits", on_delete=models.CASCADE)
    split_sequence = models.PositiveSmallIntegerField()
    planned_date = models.DateField()
    quantity = models.PositiveIntegerField()

    class Meta:
        ordering = ['split_sequence']

    def __str__(self):
        return f"{self.order.order_number} — split #{self.split_sequence}"
