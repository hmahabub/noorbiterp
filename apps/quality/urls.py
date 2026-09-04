from django.urls import path

from . import views

app_name = 'quality'

urlpatterns = [
    path('', views.InspectionListView.as_view(), name='list'),
    path('add/', views.InspectionCreateView.as_view(), name='create'),
    path('<int:pk>/', views.InspectionDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.InspectionUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.InspectionDeleteView.as_view(), name='delete'),
]
