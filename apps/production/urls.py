from django.urls import path

from . import views

app_name = 'production'

urlpatterns = [
    path('', views.ProductionListView.as_view(), name='list'),
    path('add/', views.ProductionCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ProductionDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ProductionUpdateEditView.as_view(), name='update'),
    path('<int:pk>/delete/', views.ProductionDeleteView.as_view(), name='delete'),
]
