import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from datetime import date, timedelta
from apps.users.models import Department, User
from apps.buyers.models import Buyer, BuyerContact, BuyerShipTo
from apps.factories.models import Factory
from apps.orders.models import Order, OrderItem, OrderItemBreakdown
from apps.samples.models import SamplePO
from apps.finance.models import Commission
from apps.items.models import Item, FinishedItem, FinishedItemVariant

depts = {}
for name in ["Buyer", "Sales", "Merchandising", "Accounts", "Commercial", "Quality", "Follow-up"]:
    d, _ = Department.objects.get_or_create(name=name)
    depts[name] = d

if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "admin12345", is_md=True, department=depts["Sales"])
    print("Created superuser: admin / admin12345 (MD)")

buyer, _ = Buyer.objects.get_or_create(
    code="BY-001", defaults=dict(name="Nordic Kids Wear", country="Denmark", buyer_type="international",
    category="brand", currency="EUR", commission_rate=5)
)
BuyerContact.objects.get_or_create(buyer=buyer, name="Anna Sorensen", defaults=dict(designation="Sourcing Manager", email="anna@nordickids.example"))
ship_to, _ = BuyerShipTo.objects.get_or_create(
    buyer=buyer, label="Main Warehouse",
    defaults=dict(address_line1="4921 Eastern Ave.", city="Bell", state="CA", postal_code="90201",
                  country="USA", phone="323-264-3000", is_default=True)
)

factory, _ = Factory.objects.get_or_create(name="Padma Garments Ltd.", defaults=dict(location="Chattogram, BD", factory_type="garment"))

# Finished item catalogue (buyer-facing style) + color/size variants
finished_item, _ = FinishedItem.objects.get_or_create(
    buyer_style="WS806G318",
    defaults=dict(type="shorts", description="POLY CARGO SHORT (SEAN)",
                  content="100% POLYESTER SOLID T400 75D X 75D/2 / 132x81 130 gsm",
                  finish="NW", unit_price="3.1500")
)
variant_specs = [("BLACK", "S"), ("BLACK", "M"), ("LODEN", "S"), ("MIRAGE GREY", "M")]
for color, size in variant_specs:
    FinishedItemVariant.objects.get_or_create(finished_item=finished_item, color_name=color, size=size)

order, created = Order.objects.get_or_create(
    buyer_order_number="WC6824",
    defaults=dict(buyer=buyer, ship_to=ship_to, factory=factory, order_type="bulk", status="in_production",
                  currency="USD", required_ship_date=date.today() - timedelta(days=2))
)

order_item, _ = OrderItem.objects.get_or_create(
    order=order, item=finished_item, defaults=dict(qty=4800, unit_price="3.1500", pack="A")
)
breakdown_specs = [("BLACK", "S", 800), ("BLACK", "M", 1600), ("LODEN", "S", 600), ("MIRAGE GREY", "M", 1400)]
for color, size, qty in breakdown_specs:
    variant = FinishedItemVariant.objects.get(finished_item=finished_item, color_name=color, size=size)
    OrderItemBreakdown.objects.get_or_create(
        order_item=order_item, variant=variant, defaults=dict(qty=qty, unit_price="3.1500")
    )

SamplePO.objects.get_or_create(
    po_number="SPO-2026-0001",
    defaults=dict(buyer=buyer, factory=factory, sample_type="pp", fabric_source="factory",
                  status="pending_submission", requested_date=date.today() - timedelta(days=10),
                  submission_date=date.today() - timedelta(days=2))
)

Commission.objects.get_or_create(
    buyer=buyer, order=order, defaults=dict(rate=5, amount=1200, currency="USD", due_date=date.today() - timedelta(days=5))
)

fabric_supplier, _ = Factory.objects.get_or_create(
    name="Silk Route Fabrics Ltd.", defaults=dict(location="Dhaka, BD", factory_type="material_supplier")
)
Item.objects.get_or_create(
    supplier_code="FB-CTN-001",
    defaults=dict(type="fabric", description="100% Cotton Jersey 180gsm", color="White",
                  unit_price="3.2500", unit="mtr", supplier=fabric_supplier)
)
Item.objects.get_or_create(
    supplier_code="TR-BTN-014",
    defaults=dict(type="trims", description="4-hole Poly Button 15L", size="15L", color="Natural",
                  unit_price="0.0150", unit="pcs", supplier=fabric_supplier)
)

from apps.costing.models import StandardBOMLine

# Standard BOM for the WS806G318 style — the "standard" recipe that gets
# cloned (and qty-scaled) onto every order line for this style.
StandardBOMLine.objects.get_or_create(
    finished_item=finished_item, item=Item.objects.get(supplier_code="FB-CTN-001"),
    defaults=dict(category="fabric", consumption="1.2500", unit="mtr", wastage_percent="5.00", unit_price="3.2500")
)
StandardBOMLine.objects.get_or_create(
    finished_item=finished_item, item=Item.objects.get(supplier_code="TR-BTN-014"),
    defaults=dict(category="trims", consumption="6", unit="pcs", wastage_percent="2.00", unit_price="0.0150")
)

print("Seed data created.")