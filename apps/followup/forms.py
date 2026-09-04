from django import forms

from .models import FollowUpEntry


class FollowUpEntryForm(forms.ModelForm):
    class Meta:
        model = FollowUpEntry
        fields = ['order', 'followup_type', 'lc_status', 'condition', 'ready_quantity', 'remarks']
        widgets = {'remarks': forms.Textarea(attrs={'rows': 2})}
