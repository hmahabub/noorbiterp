from django import forms

from .models import Inspection


class InspectionForm(forms.ModelForm):
    class Meta:
        model = Inspection
        fields = ['order', 'aql', 'inspector', 'inspection_date', 'result']
        widgets = {'inspection_date': forms.DateInput(attrs={'type': 'date'})}
