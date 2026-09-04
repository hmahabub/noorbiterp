from django.urls import path

from . import views

app_name = 'purchase_orders'

urlpatterns = [
    path('', views.PurchaseOrderListView.as_view(), name='list'),
    path('add/', views.PurchaseOrderCreateView.as_view(), name='create'),
    path('<int:pk>/', views.PurchaseOrderDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.PurchaseOrderUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.PurchaseOrderDeleteView.as_view(), name='delete'),

    path('<int:po_pk>/add-item/', views.AddPOItemView.as_view(), name='add_item'),
    path('<int:po_pk>/remove-item/<int:pk>/', views.remove_po_item, name='remove_item'),

    path('<int:pk>/submit/', views.submit_for_approval, name='submit'),
    path('<int:pk>/pdf/', views.print_po, name='pdf'),
]
