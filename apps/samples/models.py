from datetime import timedelta

from django.db import models
from django.utils import timezone


class SamplePO(models.Model):
    SAMPLE_TYPE = [("proto", "Proto"), ("fit", "Fit Sample"), ("pp", "PP Sample")]
    SOURCE = [("buyer", "Buyer-sourced"), ("factory", "Factory-sourced")]
    STATUS = [("running", "Running"), ("pending_submission", "Pending Submission"),
              ("delivered", "Delivered"), ("critical", "Critical"), ("archived", "Archived")]

    po_number = models.CharField(max_length=30, unique=True)
    buyer = models.ForeignKey("buyers.Buyer", on_delete=models.PROTECT, related_name="sample_pos")
    factory = models.ForeignKey("factories.Factory", on_delete=models.PROTECT, related_name="sample_pos")
    sample_type = models.CharField(max_length=10, choices=SAMPLE_TYPE)
    fabric_source = models.CharField(max_length=10, choices=SOURCE)
    is_paid = models.BooleanField(default=False)  # P number highlight
    p_number = models.CharField(max_length=30, blank=True)
    development_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="pending_submission")
    requested_date = models.DateField()
    submission_date = models.DateField(null=True, blank=True)
    delivered_date = models.DateField(null=True, blank=True)
    md_approved = models.BooleanField(default=False)  # MD approval gate before proceeding

    class Meta:
        ordering = ['-requested_date']
        verbose_name = "Sample PO"

    def __str__(self):
        return self.po_number

    @property
    def is_critical(self):
        """Past submission date and still pending -> surfaced on the dashboard widget."""
        return (
            self.status == "pending_submission"
            and self.submission_date is not None
            and timezone.now().date() > self.submission_date
        )

    def archive_if_due(self):
        """Called by the daily archive task: 21 days after delivery -> archived."""
        if self.status == "delivered" and self.delivered_date:
            if timezone.now().date() >= self.delivered_date + timedelta(days=21):
                self.status = "archived"
                self.save(update_fields=["status"])


class SampleItem(models.Model):
    sample_po = models.ForeignKey(SamplePO, related_name="items", on_delete=models.CASCADE)
    style = models.CharField(max_length=50)
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=20, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.style} / {self.color} / {self.size}"
