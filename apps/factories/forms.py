from django import forms

from .models import Factory


class FactoryForm(forms.ModelForm):
    class Meta:
        model = Factory
        fields = ['name', 'location', 'factory_type', 'is_active']
