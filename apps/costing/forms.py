from django import forms

from .models import CostingLine, CostingSheet


class CostingSheetForm(forms.ModelForm):
    class Meta:
        model = CostingSheet
        fields = ['order_item', 'version', 'currency', 'status', 'approved_by']


class CostingLineForm(forms.ModelForm):
    class Meta:
        model = CostingLine
        fields = [
            'category', 'component_name', 'description', 'supplier_info',
            'unit_price', 'consumption', 'wastage_percent', 'cost',
        ]
        widgets = {
            'component_name': forms.TextInput(attrs={'autofocus': True}),
            'description': forms.TextInput(),
            'supplier_info': forms.TextInput(),
            'unit_price': forms.NumberInput(attrs={'step': '0.0001', 'class': 'bom-unit-price'}),
            'consumption': forms.NumberInput(attrs={'step': '0.0001', 'class': 'bom-consumption'}),
            'wastage_percent': forms.NumberInput(attrs={'step': '0.01', 'class': 'bom-wastage'}),
            'cost': forms.NumberInput(attrs={'step': '0.0001', 'class': 'bom-cost'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit_price'].required = False
        self.fields['consumption'].required = False
        self.fields['wastage_percent'].required = False
        self.fields['wastage_percent'].help_text = "e.g. 5 for 5%. Leave blank for flat-cost rows like CM or Profit Margin."
        self.fields['cost'].help_text = "Auto-suggested from Unit Price x Consumption x (1 + Wastage%) — always editable."
