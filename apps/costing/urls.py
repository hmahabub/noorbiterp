from django.urls import path

from . import views

app_name = 'costing'

urlpatterns = [
    path('', views.CostingListView.as_view(), name='list'),
    path('add/', views.CostingCreateView.as_view(), name='create'),
    path('<int:pk>/', views.CostingDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.CostingUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.CostingDeleteView.as_view(), name='delete'),

    # Unified BOM + Costing interface
    path('order-item/<int:order_item_pk>/', views.open_order_item_costing, name='order_item_costing'),
    path('sheet/<int:pk>/', views.CostingSheetView.as_view(), name='sheet'),
    path('sheet/<int:pk>/print/', views.print_costing_sheet, name='print'),
    path('sheet/<int:pk>/excel/', views.download_costing_excel, name='excel'),
    path('line/<int:pk>/delete/', views.delete_costing_line, name='delete_line'),
]
