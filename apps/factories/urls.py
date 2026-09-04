from django.urls import path

from . import views

app_name = 'factories'

urlpatterns = [
    path('', views.FactoryListView.as_view(), name='list'),
    path('add/', views.FactoryCreateView.as_view(), name='create'),
    path('<int:pk>/', views.FactoryDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.FactoryUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.FactoryDeleteView.as_view(), name='delete'),
]
