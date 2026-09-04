from django.urls import path

from . import views

app_name = 'finance'

urlpatterns = [
    # Commission
    path('commission/', views.CommissionListView.as_view(), name='commission_list'),
    path('commission/add/', views.CommissionCreateView.as_view(), name='commission_create'),
    path('commission/<int:pk>/', views.CommissionDetailView.as_view(), name='commission_detail'),
    path('commission/<int:pk>/edit/', views.CommissionUpdateView.as_view(), name='commission_update'),
    path('commission/<int:pk>/delete/', views.CommissionDeleteView.as_view(), name='commission_delete'),

    # Expense
    path('expense/', views.ExpenseListView.as_view(), name='expense_list'),
    path('expense/add/', views.ExpenseCreateView.as_view(), name='expense_create'),
    path('expense/<int:pk>/', views.ExpenseDetailView.as_view(), name='expense_detail'),
    path('expense/<int:pk>/edit/', views.ExpenseUpdateView.as_view(), name='expense_update'),
    path('expense/<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='expense_delete'),

    # Payment
    path('payment/', views.PaymentListView.as_view(), name='payment_list'),
    path('payment/add/', views.PaymentCreateView.as_view(), name='payment_create'),
    path('payment/<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('payment/<int:pk>/edit/', views.PaymentUpdateView.as_view(), name='payment_update'),
    path('payment/<int:pk>/delete/', views.PaymentDeleteView.as_view(), name='payment_delete'),
]
