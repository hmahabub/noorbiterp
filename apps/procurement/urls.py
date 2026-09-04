from django.urls import path

from . import views

app_name = 'procurement'

urlpatterns = [
    path('', views.SupplierPOListView.as_view(), name='list'),
    path('add/', views.SupplierPOCreateView.as_view(), name='create'),
    path('<int:pk>/', views.SupplierPODetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.SupplierPOUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.SupplierPODeleteView.as_view(), name='delete'),
]
