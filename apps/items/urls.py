from django.urls import path

from . import views

app_name = 'items'

urlpatterns = [
    # Raw material / trim items
    path('', views.ItemListView.as_view(), name='list'),
    path('add/', views.ItemCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ItemDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ItemUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.ItemDeleteView.as_view(), name='delete'),

    # Finished items (buyer-facing styles)
    path('finished/', views.FinishedItemListView.as_view(), name='finished_list'),
    path('finished/add/', views.FinishedItemCreateView.as_view(), name='finished_create'),
    path('finished/<int:pk>/', views.FinishedItemDetailView.as_view(), name='finished_detail'),
    path('finished/<int:pk>/edit/', views.FinishedItemUpdateView.as_view(), name='finished_update'),
    path('finished/<int:pk>/delete/', views.FinishedItemDeleteView.as_view(), name='finished_delete'),

    path('finished/<int:finished_item_pk>/add-variant/', views.AddFinishedItemVariantView.as_view(), name='finished_add_variant'),
    path('finished/<int:finished_item_pk>/remove-variant/<int:pk>/', views.remove_finished_item_variant, name='finished_remove_variant'),
]
