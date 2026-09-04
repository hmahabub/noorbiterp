from django.urls import path

from . import views

app_name = 'followup'

urlpatterns = [
    path('', views.FollowUpListView.as_view(), name='list'),
    path('add/', views.FollowUpCreateView.as_view(), name='create'),
    path('<int:pk>/', views.FollowUpDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.FollowUpUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.FollowUpDeleteView.as_view(), name='delete'),
]
