from django.db import models


class Commission(models.Model):
    STATUS = [("pending", "Pending"), ("partial", "Partially Received"), ("received", "Received")]

    buyer = models.ForeignKey("buyers.Buyer", on_delete=models.PROTECT, related_name="commissions")
    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, related_name="commissions")
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=5, default="USD")
    due_date = models.DateField()
    received_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS, default="pending")

    class Meta:
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.order.order_number} — {self.amount} {self.currency}"

    @property
    def outstanding(self):
        return self.amount - self.received_amount


class Expense(models.Model):
    date = models.DateField()
    category = models.CharField(max_length=50)
    buyer = models.ForeignKey("buyers.Buyer", null=True, blank=True, on_delete=models.SET_NULL, related_name="expenses")
    order = models.ForeignKey("orders.Order", null=True, blank=True, on_delete=models.SET_NULL, related_name="expenses")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=5, default="USD")
    vendor = models.CharField(max_length=150, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    approval_status = models.CharField(max_length=15, default="pending")

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.category} — {self.amount} {self.currency}"


class Payment(models.Model):
    TYPE = [("received", "Money Received"), ("paid", "Money Paid"), ("bank_transfer", "Bank Transaction")]

    date = models.DateField()
    transaction_type = models.CharField(max_length=15, choices=TYPE)
    buyer = models.ForeignKey("buyers.Buyer", null=True, blank=True, on_delete=models.SET_NULL, related_name="payments")
    vendor = models.ForeignKey("factories.Factory", null=True, blank=True, on_delete=models.SET_NULL, related_name="payments")
    order = models.ForeignKey("orders.Order", null=True, blank=True, on_delete=models.SET_NULL, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=5, default="USD")
    bank_account = models.CharField(max_length=100, blank=True)
    reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=15, default="completed")

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_transaction_type_display()} — {self.amount} {self.currency}"


class ProfitabilityRecord(models.Model):
    """Materialized snapshot; in Phase 1 recomputed on-demand via `refresh()`.
    In production this would be triggered by a Celery task on save of
    Commission/Expense/Claim/Payment for the order (see project plan 4.10)."""
    order = models.OneToOneField("orders.Order", related_name="profitability", on_delete=models.CASCADE)
    revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expense = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    claim_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    contribution = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    contribution_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profitability — {self.order.order_number}"

    def refresh(self):
        from apps.quality.models import Claim
        self.commission = sum((c.amount for c in self.order.commissions.all()), 0)
        self.expense = sum((e.amount for e in self.order.expenses.all()), 0)
        self.claim_deduction = sum((c.amount for c in Claim.objects.filter(order=self.order)), 0)
        self.contribution = self.commission - self.expense - self.claim_deduction
        self.contribution_percentage = (
            (self.contribution / self.revenue * 100) if self.revenue else 0
        )
        self.save()
