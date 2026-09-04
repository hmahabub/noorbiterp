from django.urls import path

from . import views

app_name = 'samples'

urlpatterns = [
    path('', views.SampleListView.as_view(), name='list'),
    path('add/', views.SampleCreateView.as_view(), name='create'),
    path('<int:pk>/', views.SampleDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.SampleUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.SampleDeleteView.as_view(), name='delete'),
]
