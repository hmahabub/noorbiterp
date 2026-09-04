from django import forms

from .models import Shipment


class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ['order', 'quantity', 'planned_ship_date', 'mode', 'status', 'vessel', 'container', 'etd', 'eta']
        widgets = {
            'planned_ship_date': forms.DateInput(attrs={'type': 'date'}),
            'etd': forms.DateInput(attrs={'type': 'date'}),
            'eta': forms.DateInput(attrs={'type': 'date'}),
        }
