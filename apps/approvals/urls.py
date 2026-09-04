from django.urls import path

from . import views

app_name = 'approvals'

urlpatterns = [
    path('mine/', views.MyApprovalsView.as_view(), name='my_approvals'),
    path('<int:pk>/<str:decision>/', views.decide_approval, name='decide'),
]
