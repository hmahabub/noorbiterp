from django import forms

from .models import FinishedItem, FinishedItemVariant, Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['type', 'supplier_code', 'description', 'size', 'color', 'unit_price', 'unit', 'supplier']

    def clean_buyer_code(self):
        supplier_code = self.cleaned_data.get('supplier_code')
        if Item.objects.filter(supplier_code=supplier_code).exists():
            raise ValidationError("This supplier code is already in use.")
        return supplier_code

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FinishedItemForm(forms.ModelForm):
    class Meta:
        model = FinishedItem
        fields = ['type', 'buyer_style', 'description', 'content', 'finish', 'unit_price']
        widgets = {'content': forms.Textarea(attrs={'rows': 3})}


class FinishedItemVariantForm(forms.ModelForm):
    class Meta:
        model = FinishedItemVariant
        fields = ['color_name', 'size', 'is_active', 'status']

