from django import forms

from .models import ProductionUpdate


class ProductionUpdateForm(forms.ModelForm):
    class Meta:
        model = ProductionUpdate
        fields = ['order', 'stage', 'quantity_completed', 'lc_status', 'condition', 'ready_quantity', 'remarks']
        widgets = {'remarks': forms.Textarea(attrs={'rows': 2})}
