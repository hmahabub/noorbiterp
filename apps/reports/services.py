"""Each of the 10 monthly reports (project plan §4.12) is a function here.
Phase 1 renders them on demand as an HTML page; Phase 4 adds the scheduled
Celery Beat + PDF/Excel export described in the plan."""
from django.utils import timezone

REPORT_REGISTRY = [
    {"slug": "business-summary", "name": "Business Summary"},
    {"slug": "sales-commission", "name": "Sales & Commission"},
    {"slug": "order-performance", "name": "Order Performance"},
    {"slug": "financial-performance", "name": "Financial Performance"},
    {"slug": "buyer-performance", "name": "Buyer Performance"},
    {"slug": "factory-performance", "name": "Factory Performance"},
    {"slug": "merchandising-performance", "name": "Merchandising Performance"},
    {"slug": "quality-shipment", "name": "Quality & Shipment"},
    {"slug": "risk-control", "name": "Risk & Control"},
    {"slug": "management-summary", "name": "Management Summary"},
]


def generate_report(slug):
    from apps.orders.models import Order
    from apps.buyers.models import Buyer
    from apps.factories.models import Factory
    from apps.finance.models import Commission, Expense, Payment
    from apps.quality.models import Inspection, Claim
    from apps.shipment.models import Shipment

    today = timezone.now().date()
    ctx = {"generated_at": today}

    if slug == "business-summary":
        ctx["rows"] = [
            ("Total Buyers", Buyer.objects.count()),
            ("Total Factories", Factory.objects.count()),
            ("Total Orders", Order.objects.count()),
            ("Running Orders", Order.objects.exclude(status__in=["completed", "cancelled"]).count()),
        ]
    elif slug == "sales-commission":
        ctx["rows"] = [(c.order.order_number, c.buyer.name, c.amount, c.currency, c.status) for c in Commission.objects.all()[:50]]
        ctx["headers"] = ["Order", "Buyer", "Amount", "Currency", "Status"]
    elif slug == "order-performance":
        ctx["rows"] = [(o.order_number, o.buyer.name, o.status, o.required_ship_date) for o in Order.objects.all()[:50]]
        ctx["headers"] = ["Order", "Buyer", "Status", "Required Ship Date"]
    elif slug == "financial-performance":
        ctx["rows"] = [
            ("Total Commission", sum((c.amount for c in Commission.objects.all()), 0)),
            ("Total Expense", sum((e.amount for e in Expense.objects.all()), 0)),
            ("Total Payments", sum((p.amount for p in Payment.objects.all()), 0)),
        ]
    elif slug == "buyer-performance":
        ctx["rows"] = [(b.name, b.country, b.performance["total_orders"], b.performance["running_orders"]) for b in Buyer.objects.all()[:50]]
        ctx["headers"] = ["Buyer", "Country", "Total Orders", "Running Orders"]
    elif slug == "factory-performance":
        ctx["rows"] = [(f.name, f.factory_type, f.orders.count()) for f in Factory.objects.all()[:50]]
        ctx["headers"] = ["Factory", "Type", "Orders"]
    elif slug == "merchandising-performance":
        ctx["rows"] = [(o.order_number, o.style, o.status) for o in Order.objects.exclude(status='completed')[:50]]
        ctx["headers"] = ["Order", "Style", "Status"]
    elif slug == "quality-shipment":
        ctx["rows"] = [(i.order.order_number, i.result, i.inspection_date) for i in Inspection.objects.all()[:50]]
        ctx["headers"] = ["Order", "QC Result", "Inspection Date"]
    elif slug == "risk-control":
        ctx["rows"] = [(c.order.order_number, c.claim_type, c.amount, c.status) for c in Claim.objects.all()[:50]]
        ctx["headers"] = ["Order", "Claim Type", "Amount", "Status"]
    elif slug == "management-summary":
        ctx["rows"] = [
            ("Active Buyers", Buyer.objects.filter(is_active=True).count()),
            ("Running Orders", Order.objects.exclude(status__in=["completed", "cancelled"]).count()),
            ("Shipments this month", Shipment.objects.filter(planned_ship_date__month=today.month, planned_ship_date__year=today.year).count()),
        ]
    return ctx
