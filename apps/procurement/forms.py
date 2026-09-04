from django import forms

from .models import SupplierPO


class SupplierPOForm(forms.ModelForm):
    class Meta:
        model = SupplierPO
        fields = [
            'po_number', 'order', 'supplier', 'material_type', 'booking_date',
            'expected_receiving_date', 'actual_receiving_date', 'status',
        ]
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_receiving_date': forms.DateInput(attrs={'type': 'date'}),
            'actual_receiving_date': forms.DateInput(attrs={'type': 'date'}),
        }
