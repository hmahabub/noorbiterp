from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

admin.site.site_header = "Garment ERP Administration"
admin.site.site_title = "Garment ERP Admin"
admin.site.index_title = "Data Entry & System Administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='dashboard:home', permanent=False)),
    path('accounts/', include('apps.users.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('buyers/', include('apps.buyers.urls')),
    path('items/', include('apps.items.urls')),
    path('factories/', include('apps.factories.urls')),
    path('samples/', include('apps.samples.urls')),
    path('orders/', include('apps.orders.urls')),
    path('costing/', include('apps.costing.urls')),
    path('procurement/', include('apps.procurement.urls')),
    path('production/', include('apps.production.urls')),
    path('purchase-orders/', include('apps.purchase_orders.urls')),
    path('quality/', include('apps.quality.urls')),
    path('shipment/', include('apps.shipment.urls')),
    path('finance/', include('apps.finance.urls')),
    path('followup/', include('apps.followup.urls')),
    path('reports/', include('apps.reports.urls')),
    path('approvals/', include('apps.approvals.urls')),
    path('documents/', include('apps.documents.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
