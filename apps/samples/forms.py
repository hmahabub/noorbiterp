from django import forms

from .models import SamplePO


class SamplePOForm(forms.ModelForm):
    class Meta:
        model = SamplePO
        fields = [
            'po_number', 'buyer', 'factory', 'sample_type', 'fabric_source', 'is_paid',
            'p_number', 'development_charge', 'status', 'requested_date',
            'submission_date', 'delivered_date',
        ]
        widgets = {
            'requested_date': forms.DateInput(attrs={'type': 'date'}),
            'submission_date': forms.DateInput(attrs={'type': 'date'}),
            'delivered_date': forms.DateInput(attrs={'type': 'date'}),
        }
