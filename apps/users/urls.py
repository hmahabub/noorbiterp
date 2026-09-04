from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.ERPLoginView.as_view(), name='login'),
    path('logout/', views.ERPLogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]
