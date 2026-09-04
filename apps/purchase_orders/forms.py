from django import forms

from .models import PurchaseOrder, POItem


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = [
            'to_supplier', 'destination', 'season', 'style', 'customer_po_number',
            'payment_method', 'delivery_date', 'shipping_method', 'note', 'terms_and_conditions',
        ]
        widgets = {
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 2}),
            'terms_and_conditions': forms.Textarea(attrs={'rows': 4}),
        }


class ItemSelect(forms.Select):
    """Stamps each <option> with data-price so the add-item page can
    auto-fill the unit price client-side without an extra request."""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value not in (None, ""):
            from .models import POItem  # local import avoids a circular reference
            from apps.items.models import Item
            try:
                pk = value.value if hasattr(value, "value") else value
                item = Item.objects.get(pk=pk)
                option["attrs"]["data-price"] = str(item.unit_price)
            except Item.DoesNotExist:
                pass
        return option


class POItemForm(forms.ModelForm):
    class Meta:
        model = POItem
        fields = ['item', 'qty', 'unit_price']
        widgets = {
            'item': ItemSelect(attrs={'class': 'form-select', 'id': 'id_item'}),
            'qty': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'autofocus': True}),
            'unit_price': forms.NumberInput(attrs={'step': '0.0001'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # unit_price is pre-filled from the chosen Item's default price but
        # stays editable in case this PO negotiates a different rate.
        self.fields['unit_price'].required = False
        self.fields['unit_price'].help_text = "Auto-filled from the item's default price — override if this PO uses a different rate."

