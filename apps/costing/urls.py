from django.urls import path

from . import views

app_name = 'costing'

urlpatterns = [
    path('', views.CostingListView.as_view(), name='list'),
    path('add/', views.CostingCreateView.as_view(), name='create'),
    path('<int:pk>/', views.CostingDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.CostingUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.CostingDeleteView.as_view(), name='delete'),

    # Standard BOM & Costing (per Finished Item)
    path('standard/<int:finished_item_pk>/', views.FinishedItemBOMView.as_view(), name='standard_bom'),
    path('standard/<int:finished_item_pk>/remove/<int:pk>/', views.delete_standard_bom_line, name='remove_standard_bom_line'),

    # Order-wise BOM & Costing (per Order line)
    path('order-item/<int:order_item_pk>/', views.OrderItemBOMView.as_view(), name='order_item_bom'),
    path('order-item/<int:order_item_pk>/remove/<int:pk>/', views.delete_order_item_bom_line, name='remove_order_item_bom_line'),
]
