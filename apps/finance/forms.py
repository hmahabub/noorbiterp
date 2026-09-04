from django import forms

from .models import Commission, Expense, Payment


class CommissionForm(forms.ModelForm):
    class Meta:
        model = Commission
        fields = ['buyer', 'order', 'rate', 'amount', 'currency', 'due_date', 'received_amount', 'status']
        widgets = {'due_date': forms.DateInput(attrs={'type': 'date'})}


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'category', 'buyer', 'order', 'amount', 'currency', 'vendor', 'payment_method', 'approval_status']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['date', 'transaction_type', 'buyer', 'vendor', 'order', 'amount', 'currency', 'bank_account', 'reference', 'status']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}
