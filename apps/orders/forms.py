from django import forms

from .models import Order, OrderItem, OrderItemBreakdown


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'buyer_order_number', 'buyer', 'ship_to', 'factory', 'order_type', 'status', 'currency',
            'booking_date', 'confirmed_date', 'required_ship_date', 'planned_ship_date',
            'terms_and_conditions',
        ]
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'confirmed_date': forms.DateInput(attrs={'type': 'date'}),
            'required_ship_date': forms.DateInput(attrs={'type': 'date'}),
            'planned_ship_date': forms.DateInput(attrs={'type': 'date'}),
            'terms_and_conditions': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned = super().clean()
        buyer = cleaned.get('buyer')
        ship_to = cleaned.get('ship_to')
        if buyer and ship_to and ship_to.buyer_id != buyer.id:
            self.add_error('ship_to', "This ship-to address doesn't belong to the selected buyer.")
        return cleaned


class FinishedItemSelect(forms.Select):
    """Stamps each <option> with data-price so the add-item page can
    auto-fill the unit price client-side without an extra request."""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value not in (None, ""):
            from apps.items.models import FinishedItem
            try:
                pk = value.value if hasattr(value, "value") else value
                item = FinishedItem.objects.get(pk=pk)
                option["attrs"]["data-price"] = str(item.unit_price)
            except FinishedItem.DoesNotExist:
                pass
        return option


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['item', 'pack', 'qty', 'unit_price']
        widgets = {
            'item': FinishedItemSelect(attrs={'class': 'form-select', 'id': 'id_item'}),
            'qty': forms.NumberInput(attrs={'min': '1', 'autofocus': True}),
            'unit_price': forms.NumberInput(attrs={'step': '0.0001'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit_price'].required = False
        self.fields['unit_price'].help_text = "Auto-filled from the finished item's reference price — override for this order."


class OrderItemHeaderEditForm(forms.ModelForm):
    """Editing pack/qty/unit_price of a style already on the order — the
    style itself (`item`) can't be changed here since that would invalidate
    the color/size grid; remove and re-add the line for that instead."""

    class Meta:
        model = OrderItem
        fields = ['pack', 'qty', 'unit_price']
        widgets = {
            'pack': forms.TextInput(attrs={'style': 'width: 70px;'}),
            'qty': forms.NumberInput(attrs={'min': '1', 'style': 'width: 100px;'}),
            'unit_price': forms.NumberInput(attrs={'step': '0.0001', 'style': 'width: 110px;'}),
        }


class OrderItemBreakdownForm(forms.ModelForm):
    class Meta:
        model = OrderItemBreakdown
        fields = ['variant', 'qty', 'unit_price']
        widgets = {
            'qty': forms.NumberInput(attrs={'min': '1', 'autofocus': True}),
            'unit_price': forms.NumberInput(attrs={'step': '0.0001'}),
        }

    def __init__(self, *args, order_item=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit_price'].required = False
        self.fields['unit_price'].help_text = "Auto-filled from the order item's unit price — override if this color/size is priced differently."
        if order_item is not None:
            # Only the variants that belong to this order item's finished item.
            self.fields['variant'].queryset = order_item.item.variants.filter(is_active=True)