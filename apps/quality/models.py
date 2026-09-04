from django.db import models


class Inspection(models.Model):
    RESULT = [("pending", "Pending"), ("pass", "Pass"), ("fail", "Fail")]

    order = models.ForeignKey("orders.Order", related_name="inspections", on_delete=models.CASCADE)
    aql = models.CharField(max_length=20, blank=True)
    inspector = models.CharField(max_length=100, blank=True)
    inspection_date = models.DateField(null=True, blank=True)
    result = models.CharField(max_length=10, choices=RESULT, default="pending")

    class Meta:
        ordering = ['-inspection_date']

    def __str__(self):
        return f"{self.order.order_number} — {self.get_result_display()}"


class Claim(models.Model):
    order = models.ForeignKey("orders.Order", related_name="claims", on_delete=models.CASCADE)
    claim_type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, default="open")
    date = models.DateField()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.order.order_number} — {self.claim_type} ({self.amount})"
