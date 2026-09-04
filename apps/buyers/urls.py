from django.urls import path

from . import views

app_name = 'buyers'

urlpatterns = [
    path('', views.BuyerListView.as_view(), name='list'),
    path('add/', views.BuyerCreateView.as_view(), name='create'),
    path('<int:pk>/', views.BuyerDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.BuyerUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.BuyerDeleteView.as_view(), name='delete'),

    path('<int:buyer_pk>/ship-to/add/', views.AddBuyerShipToView.as_view(), name='add_ship_to'),
    path('<int:buyer_pk>/ship-to/<int:pk>/remove/', views.remove_ship_to, name='remove_ship_to'),
]
