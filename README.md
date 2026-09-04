# Garment ERP — Django / Bootstrap Web App

A working implementation of the **Django ERP Project Plan** for a garments buying/trading
house: Buyers, Factories, Samples, Orders, Costing & BOM, Procurement, Production, Quality,
Shipment, Finance, Follow-up, Items & Purchase Orders (with PDF export), a live Dashboard,
and Monthly Reports — all reachable from a single top navbar.

## What's included (Phase 1 scope, functional today)

- Django 6.x project, split into 16 apps under `apps/`, matching the plan's structure
- Custom `User` model with `Department`, `is_md` / `is_gm` flags
- Generic `Document` model (file attachments) and `ApprovalRequest` / `AuditLog` models,
  usable by any module via Django's `ContentType` framework — exactly as described in the plan
- Full CRUD (list / view / add / edit / delete) for every core model, built on a small shared
  set of generic views (`apps/common/generic.py`) so the 11 business apps don't repeat
  boilerplate
- Bootstrap 5 UI with a **top navbar** linking every module (with dropdowns for the
  Sourcing group — Costing/Procurement/Production — and the Finance group —
  Commission/Expense/Payment)
- Dashboard home page pulling live KPIs (urgent orders, pending QC, overdue receivables,
  critical samples, today's shipments) exactly per the plan's `get_dashboard_kpis()` spec
- Sample PO → auto-creates an MD `ApprovalRequest`; "My Approvals" inbox to approve/reject
- 21-day sample auto-archive as a management command (`archive_samples`) — wire this to cron
  or Celery Beat in production
- The 10 monthly reports as live, on-demand HTML snapshots (`apps/reports`)
- Django Admin fully registered for every model — usable as the Phase-1 data-entry tool per
  the plan
- Red / Yellow / Green shipment-status logic as a model `@property` on `Order`, reused on the
  dashboard, order list, and detail pages
- **Items catalogue** (`apps/items`): type, supplier code, description, size, color, unit
  price, unit, and a supplier link (to `Factory`) — feeds the Purchase Order line items
- **Orders** (`apps/orders`), rebuilt around the buyer's actual PO structure: an `Order`
  header (`our_order_number` auto-generated `ORD-<year>-<id>`, `buyer_order_number` for the
  buyer's own PO number e.g. "WC6824", a `ship_to` address, optional `factory`, terms &
  conditions), then a single **"Add Items" page** — add a style, and it immediately appears
  below as a **size-curve grid**: colors down the side, sizes across the top, every active
  color/size combination auto-provisioned at qty 0 so there's nothing to "add" — just type
  quantities into the grid and press Save (any row's Save button saves the whole grid, with
  live row/column/grand-total previews as you type). Each `OrderItem` is a style line (buyer
  style, pack, qty, unit price, line total); each style's `OrderItemBreakdown` rows are its
  color/size/qty cells, matching the buyer sheet's "Color & Size Breakdown" section — the
  order detail page flags whether a style's breakdown quantities reconcile against its header
  qty, and only shows non-zero rows in that read-only summary. Buyer-facing styles and their
  color/size variants live in a new catalogue, `apps/items` → `FinishedItem` (buyer style,
  description, fabric content, finish, reference price) and `FinishedItemVariant` (color,
  size, auto-generated SKU) — distinct from the raw material/trim `Item` catalogue used on
  Purchase Orders. Buyers can now have multiple **ship-to addresses**
  (`apps/buyers` → `BuyerShipTo`), managed from the buyer detail page.
- **BOM & Costing** (`apps/costing` → `StandardBOMLine`, `OrderItemBOMLine`), added on top of the
  existing aggregate `CostingSheet`: every `FinishedItem` gets a **standard BOM** — one row per
  raw material (Category, Item, Consumption per unit, Unit, Wastage %, Total Qty, Unit Price,
  Line Cost) — reachable from the Finished Item page as "Standard BOM & Costing". This standard
  recipe is the template: opening any order line's **"BOM & Costing"** page (from the order
  detail page or the size-grid page) auto-clones it, scaling Total Qty by that line's order
  qty so it becomes the actual procurement requirement for that specific order — independently
  editable afterwards without touching the standard. Both pages use the same add-row +
  inline-edit (click to expand) + delete pattern as the rest of the app, with live cost/margin
  KPIs (standard cost vs. reference FOB price at the style level; material cost vs. revenue at
  the order-line level, rolled up to an order-level estimated margin on the order detail page).
- **Purchase Orders** (`apps/purchase_orders`): PO header (To/Destination suppliers, season,
  style, customer PO number, payment method, delivery date, shipping method, notes, terms &
  conditions) with an auto-generated `PO-<year>-<id>` number. Creating a PO routes straight
  to a dedicated **"Add Items to PO"** page where each line item's price defaults from the
  Items catalogue (editable) and the running total recalculates on the server on every add.
  "Submit for Approval" locks the PO and raises an MD `ApprovalRequest` through the same
  generic approvals flow used elsewhere; once approved, a **print-ready PO page** becomes
  available — a styled, `@media print`-aware HTML sheet (navy header, PO number badge, item
  table, totals, terms, signature block) with a "Print / Save as PDF" button that calls the
  browser's native `window.print()`. No PDF library involved — the browser's print engine
  handles PDF generation, so the layout is just plain HTML/CSS (`templates/purchase_orders/print.html`)

## What's intentionally simplified for this first build

The full plan calls for a much larger stack (DRF API, Celery + Redis for async jobs,
PostgreSQL, S3 storage, HTMX/Alpine). To hand you something that runs immediately:

- **Database**: SQLite (swap to PostgreSQL by editing `DATABASES` in `config/settings.py` —
  the models already use PostgreSQL-friendly types)
- **Async jobs**: the sample auto-archive rule ships as a management command instead of a
  Celery Beat task; the "LC expiry" and "overdue" alerts are computed live in
  `apps/dashboard/services.py` rather than scheduled
- **File storage**: local `media/` folder instead of S3 (swap via `django-storages` later)
- **No DRF/API layer yet** — this build is server-rendered Django templates + Bootstrap + a
  little vanilla JS, which was the explicit ask
- **Full BOM, double-entry ledger, multi-level approval matrix, and Store/Inventory app** are
  the same "open items" flagged in the plan's Section 8 — not built here, so they can be
  confirmed with the client before the schema is extended

None of this blocks daily use — it's exactly the "Django Admin + custom CRUD, Phase 1"
milestone described in the plan's sprint table.

## Getting started

```bash
cd erp_project
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser  # or run the seed script below
python manage.py runserver
```

Open **http://127.0.0.1:8000/** — you'll be redirected to the login page, then the dashboard.

### Optional: load demo data

A small seed script is included (one buyer, one factory, one order, one sample PO, one
commission) so the dashboard and list pages aren't empty on first run:

```bash
python seed_data.py
```

This also creates an MD superuser: **admin / admin12345** — change this password immediately
if you deploy anywhere reachable.

### Daily/scheduled task

Run this once a day (cron, Task Scheduler, or later a Celery Beat task) to auto-archive
samples delivered 21+ days ago:

```bash
python manage.py archive_samples
```

## Project layout

```
erp_project/
├── config/                  # settings, root urls, wsgi/asgi
├── apps/
│   ├── common/               # shared generic CRUD views + template tags (no models)
│   ├── users/                 # custom User, Department, login/logout
│   ├── documents/              # generic file-attachment model, used by every module
│   ├── approvals/               # generic ApprovalRequest + AuditLog
│   ├── buyers/ factories/ samples/ orders/ costing/ procurement/
│   │   production/ quality/ shipment/ finance/ followup/    # business modules
│   ├── items/                  # Item (raw materials) + FinishedItem/FinishedItemVariant
│   │                            # (buyer styles + color/size, used on Orders)
│   ├── purchase_orders/        # PO header + line items + approval + print/PDF export
│   ├── dashboard/              # KPI aggregation, no models of its own
│   └── reports/                # the 10 monthly reports
├── templates/
│   ├── base.html               # top navbar + page shell
│   ├── crud/                   # generic list/detail/form/delete templates
│   ├── buyers/                 # buyer detail page (contacts + ship-to addresses)
│   ├── items/                  # finished-item detail + add-variant workflow page
│   ├── orders/                 # order detail + add-item + add-variant workflow pages
│   └── purchase_orders/        # PO detail + "add item to PO" workflow page
├── static/
│   ├── css/style.css           # custom navy/teal ERP theme (not default Bootstrap blue)
│   └── js/app.js
├── seed_data.py
└── requirements.txt
```

## Extending it

- **Add DRF**: add `rest_framework` to `INSTALLED_APPS`, add an `api/` package per app with
  serializers/viewsets, as sketched in the original plan
- **Add Celery**: add `config/celery.py`, move `archive_samples` and dashboard alert
  computation into scheduled tasks
- **Add BOM / double-entry ledger / partial receipts / Store app**: these are additive per
  the plan's Section 8 — new models + migrations, no changes to existing schema needed