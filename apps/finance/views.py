from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from apps.common.generic import CrudCreateView, CrudDeleteView, CrudDetailView, CrudListView, CrudUpdateView

from .forms import CommissionForm, ExpenseForm, PaymentForm
from .models import Commission, Expense, Payment


# ---------- Commission ----------
class CommissionListView(CrudListView, ListView):
    model = Commission
    title = 'Commissions'
    app_label = 'finance'
    list_fields = ['order', 'buyer', 'amount', 'currency', 'status', 'due_date']

    def get_url_names(self):
        return {'list': 'finance:commission_list', 'detail': 'finance:commission_detail',
                 'create': 'finance:commission_create', 'update': 'finance:commission_update',
                 'delete': 'finance:commission_delete'}


class CommissionDetailView(CrudDetailView, DetailView):
    model = Commission
    title = 'Commissions'
    app_label = 'finance'

    def get_url_names(self):
        return CommissionListView.get_url_names(self)


class CommissionCreateView(CrudCreateView, CreateView):
    model = Commission
    form_class = CommissionForm
    title = 'Add Commission'
    app_label = 'finance'

    def get_url_names(self):
        return CommissionListView.get_url_names(self)


class CommissionUpdateView(CrudUpdateView, UpdateView):
    model = Commission
    form_class = CommissionForm
    title = 'Edit Commission'
    app_label = 'finance'

    def get_url_names(self):
        return CommissionListView.get_url_names(self)


class CommissionDeleteView(CrudDeleteView, DeleteView):
    model = Commission
    app_label = 'finance'

    def get_url_names(self):
        return CommissionListView.get_url_names(self)


# ---------- Expense ----------
class ExpenseListView(CrudListView, ListView):
    model = Expense
    title = 'Expenses'
    app_label = 'finance'
    list_fields = ['category', 'order', 'buyer', 'amount', 'currency', 'approval_status']

    def get_url_names(self):
        return {'list': 'finance:expense_list', 'detail': 'finance:expense_detail',
                 'create': 'finance:expense_create', 'update': 'finance:expense_update',
                 'delete': 'finance:expense_delete'}


class ExpenseDetailView(CrudDetailView, DetailView):
    model = Expense
    title = 'Expenses'
    app_label = 'finance'

    def get_url_names(self):
        return ExpenseListView.get_url_names(self)


class ExpenseCreateView(CrudCreateView, CreateView):
    model = Expense
    form_class = ExpenseForm
    title = 'Add Expense'
    app_label = 'finance'

    def get_url_names(self):
        return ExpenseListView.get_url_names(self)


class ExpenseUpdateView(CrudUpdateView, UpdateView):
    model = Expense
    form_class = ExpenseForm
    title = 'Edit Expense'
    app_label = 'finance'

    def get_url_names(self):
        return ExpenseListView.get_url_names(self)


class ExpenseDeleteView(CrudDeleteView, DeleteView):
    model = Expense
    app_label = 'finance'

    def get_url_names(self):
        return ExpenseListView.get_url_names(self)


# ---------- Payment ----------
class PaymentListView(CrudListView, ListView):
    model = Payment
    title = 'Payments'
    app_label = 'finance'
    list_fields = ['transaction_type', 'order', 'buyer', 'vendor', 'amount', 'currency', 'status']

    def get_url_names(self):
        return {'list': 'finance:payment_list', 'detail': 'finance:payment_detail',
                 'create': 'finance:payment_create', 'update': 'finance:payment_update',
                 'delete': 'finance:payment_delete'}


class PaymentDetailView(CrudDetailView, DetailView):
    model = Payment
    title = 'Payments'
    app_label = 'finance'

    def get_url_names(self):
        return PaymentListView.get_url_names(self)


class PaymentCreateView(CrudCreateView, CreateView):
    model = Payment
    form_class = PaymentForm
    title = 'Add Payment'
    app_label = 'finance'

    def get_url_names(self):
        return PaymentListView.get_url_names(self)


class PaymentUpdateView(CrudUpdateView, UpdateView):
    model = Payment
    form_class = PaymentForm
    title = 'Edit Payment'
    app_label = 'finance'

    def get_url_names(self):
        return PaymentListView.get_url_names(self)


class PaymentDeleteView(CrudDeleteView, DeleteView):
    model = Payment
    app_label = 'finance'

    def get_url_names(self):
        return PaymentListView.get_url_names(self)
