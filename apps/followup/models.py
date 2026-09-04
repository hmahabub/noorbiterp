from django.db import models


class FollowUpEntry(models.Model):
    TYPE = [("sample", "Sample"), ("bulk", "Bulk")]

    order = models.ForeignKey("orders.Order", related_name="followups", on_delete=models.CASCADE)
    followup_type = models.CharField(max_length=10, choices=TYPE)
    date = models.DateField(auto_now_add=True)
    lc_status = models.CharField(max_length=50, blank=True)
    condition = models.CharField(max_length=100, blank=True)
    ready_quantity = models.PositiveIntegerField(default=0)
    remarks = models.TextField(blank=True)
    updated_by = models.ForeignKey("users.User", on_delete=models.PROTECT)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Follow-up entries"

    def __str__(self):
        return f"{self.order.order_number} — {self.get_followup_type_display()} ({self.date})"
