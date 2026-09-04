from django import forms

from .models import Buyer, BuyerContact, BuyerRequirement, BuyerShipTo


class BuyerForm(forms.ModelForm):
    class Meta:
        model = Buyer
        fields = [
            'code', 'name', 'country', 'city', 'website', 'brand', 'buyer_type', 'category',
            'is_active', 'currency', 'payment_terms', 'credit_limit', 'incoterms',
            'payment_method', 'commission_rate', 'default_factory', 'remarks',
        ]
        widgets = {'remarks': forms.Textarea(attrs={'rows': 3}),
                    'code': forms.TextInput(attrs={'readonly': 'readonly'})
        }

    def clean_buyer_code(self):
        code = self.cleaned_data.get('code')
        if Buyer.objects.filter(code=code).exists():
            raise ValidationError("This code is already in use.")
        return code

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # Only for creation
            prefix = f"BY"
            count = Buyer.objects.all().count() + 1
            next_code = f"{prefix}-{count:04d}"
            self.fields['code'].initial = next_code


class BuyerContactForm(forms.ModelForm):
    class Meta:
        model = BuyerContact
        fields = '__all__'


class BuyerRequirementForm(forms.ModelForm):
    class Meta:
        model = BuyerRequirement
        exclude = ['buyer']
        widgets = {f: forms.Textarea(attrs={'rows': 2}) for f in [
            'packaging_requirement', 'label_requirement', 'poly_requirement',
            'fabric_preference', 'special_requirement', 'inspection_requirement']}

class BuyerShipToForm(forms.ModelForm):
    class Meta:
        model = BuyerShipTo
        fields = [
            'label', 'address_line1', 'address_line2', 'city', 'state',
            'postal_code', 'country', 'phone', 'is_default',
        ]

