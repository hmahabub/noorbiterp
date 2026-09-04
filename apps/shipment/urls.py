from django.urls import path

from . import views

app_name = 'shipment'

urlpatterns = [
    path('', views.ShipmentListView.as_view(), name='list'),
    path('add/', views.ShipmentCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ShipmentDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ShipmentUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.ShipmentDeleteView.as_view(), name='delete'),
]
