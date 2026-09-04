from django.urls import path

from . import views

app_name = 'documents'

urlpatterns = [
    path('upload/<int:content_type_id>/<int:object_id>/', views.DocumentUploadView.as_view(), name='upload'),
    path('<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='delete'),
]
