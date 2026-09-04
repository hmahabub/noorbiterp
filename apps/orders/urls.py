from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='list'),
    path('add/', views.OrderCreateView.as_view(), name='create'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.OrderUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.OrderDeleteView.as_view(), name='delete'),

    path('<int:order_pk>/add-item/', views.AddOrderItemView.as_view(), name='add_item'),
    path('<int:order_pk>/remove-item/<int:pk>/', views.remove_order_item, name='remove_item'),
    path('<int:order_pk>/remove-variant/<int:pk>/', views.remove_order_item_variant_inline, name='remove_variant_inline'),

    path('item/<int:order_item_pk>/add-variant/', views.AddOrderItemVariantView.as_view(), name='add_variant'),
    path('item/<int:order_item_pk>/remove-variant/<int:pk>/', views.remove_order_item_variant, name='remove_variant'),
]
