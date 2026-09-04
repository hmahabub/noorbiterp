from django import forms

from apps.items.models import Item

from .models import CostingSheet, OrderItemBOMLine, StandardBOMLine


class CostingSheetForm(forms.ModelForm):
    class Meta:
        model = CostingSheet
        fields = [
            'order', 'version', 'fabric_cost', 'trims_cost', 'cm_cost',
            'washing_cost', 'freight_cost', 'currency', 'status', 'approved_by',
        ]


class RawItemSelect(forms.Select):
    """Stamps each <option> with data-price/data-unit so BOM pages can
    auto-fill unit price and unit client-side when a raw material is picked."""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value not in (None, ""):
            try:
                pk = value.value if hasattr(value, "value") else value
                item = Item.objects.get(pk=pk)
                option["attrs"]["data-price"] = str(item.unit_price)
                option["attrs"]["data-unit"] = item.unit
                option["attrs"]["data-category"] = item.type
            except Item.DoesNotExist:
                pass
        return option


class StandardBOMLineForm(forms.ModelForm):
    class Meta:
        model = StandardBOMLine
        fields = ['category', 'item', 'consumption', 'unit', 'wastage_percent', 'unit_price']
        widgets = {
            'item': RawItemSelect(attrs={'class': 'form-select', 'id': 'id_item'}),
            'consumption': forms.NumberInput(attrs={'step': '0.0001', 'min': '0', 'autofocus': True}),
            'wastage_percent': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'unit_price': forms.NumberInput(attrs={'step': '0.0001'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit_price'].required = False
        self.fields['unit_price'].help_text = "Auto-filled from the material's catalogue price — override if needed."
        self.fields['wastage_percent'].required = False


class OrderItemBOMLineForm(forms.ModelForm):
    class Meta:
        model = OrderItemBOMLine
        fields = ['category', 'item', 'consumption', 'unit', 'wastage_percent', 'unit_price']
        widgets = {
            'item': RawItemSelect(attrs={'class': 'form-select', 'id': 'id_item'}),
            'consumption': forms.NumberInput(attrs={'step': '0.0001', 'min': '0', 'autofocus': True}),
            'wastage_percent': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'unit_price': forms.NumberInput(attrs={'step': '0.0001'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit_price'].required = False
        self.fields['unit_price'].help_text = "Auto-filled from the material's catalogue price — override for this order."
        self.fields['wastage_percent'].required = False
