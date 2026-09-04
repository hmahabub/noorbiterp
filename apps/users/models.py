from django.contrib.auth.models import AbstractUser
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=50, unique=True)
    # Buyer, Sales, Merchandising, Accounts, Commercial, Quality, Follow-up

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class User(AbstractUser):
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, null=True, blank=True, related_name='users'
    )
    phone = models.CharField(max_length=30, blank=True)
    is_md = models.BooleanField('Managing Director', default=False)  # drives MD-only approvals & dashboard scope
    is_gm = models.BooleanField('General Manager', default=False)

    def __str__(self):
        return self.get_full_name() or self.username
