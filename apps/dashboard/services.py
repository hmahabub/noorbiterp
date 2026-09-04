"""Read-only aggregation layer — no models of its own (see project plan 4.12).
Pulls live KPIs from every business app for the MD/GM dashboard."""
from datetime import timedelta

from django.utils import timezone


def get_dashboard_kpis(user):
    from apps.buyers.models import Buyer
    from apps.orders.models import Order
    from apps.quality.models import Inspection
    from apps.finance.models import Commission
    from apps.shipment.models import Shipment
    from apps.samples.models import SamplePO

    today = timezone.now().date()

    orders = Order.objects.all()
    urgent_orders = [o for o in orders.exclude(status__in=['completed', 'cancelled']) if o.shipment_status_color == 'red']

    return {
        'active_buyers': Buyer.objects.filter(is_active=True).count(),
        'running_orders': orders.exclude(status__in=['completed', 'cancelled']).count(),
        'urgent_orders_count': len(urgent_orders),
        'urgent_orders': urgent_orders[:8],
        'pending_qc': Inspection.objects.filter(result='pending').count(),
        'overdue_receivables': Commission.objects.filter(due_date__lt=today, status__in=['pending', 'partial']),
        'overdue_receivables_count': Commission.objects.filter(due_date__lt=today, status__in=['pending', 'partial']).count(),
        'lc_expiring_soon_count': 0,  # placeholder: wire to an LC-expiry field once confirmed (open item, plan §8)
        'todays_shipments': Shipment.objects.filter(planned_ship_date=today),
        'critical_samples': [s for s in SamplePO.objects.exclude(status='archived') if s.is_critical],
        'recent_orders': orders.order_by('-created_at')[:8],
    }
