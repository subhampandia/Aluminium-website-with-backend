# Inventory Module — Setup Instructions

## 1. Copy the app into your Django project

Copy the entire `inventory/` folder into your Django project root
(same level as your other apps like `salary`, `attendance`, etc.)

## 2. Register the app in settings.py

```python
INSTALLED_APPS = [
    ...
    'inventory',
]
```

## 3. Add URLs in your main urls.py

```python
from django.urls import path, include

urlpatterns = [
    ...
    path('inventory/', include('inventory.urls')),
]
```

## 4. Run migrations

```bash
python manage.py makemigrations inventory
python manage.py migrate
```

## 5. Fix the base_template in views.py

In `inventory/views.py`, every view has this line:

```python
base_template = 'base_admin.html' if request.user.is_superuser else 'base_store.html'
```

Replace `'base_admin.html'` and `'base_store.html'` with whatever your
actual base template filenames are. For example if your admin base is
`base.html` and store manager uses the same:

```python
base_template = 'base.html'
```

Or if you pass it dynamically like other views in your project:
```python
# Match however other views in your project set base_template
base_template = get_base_template(request.user)  # your existing helper
```

## 6. Add Store Manager role to your Employee model

In your existing employee/HR app, add `STORE_MANAGER` as a role choice:

```python
ROLE_CHOICES = [
    ('HR', 'HR'),
    ('ACCOUNTS', 'Accounts'),
    ('STORE_MANAGER', 'Store Manager'),  # Add this
    ('EMPLOYEE', 'Employee'),
]
```

Then run `makemigrations` and `migrate` again.

## 7. Add Inventory links to your sidebars

In `sidebar_admin.html`, add:

```html
<div class="sidebar-heading">Inventory</div>

<a href="{% url 'inventory_dashboard' %}"
   class="{% if 'inventory' in request.path %}active{% endif %}">
    <i class="bi bi-box-seam"></i>
    <span>Inventory</span>
</a>
```

Do the same in your Store Manager sidebar template.

## 8. Base template — confirm blocks exist

Make sure ALL your base templates (admin, store manager) have these three blocks:

```html
<!-- Inside <body>, after </footer>, before logout modal -->
{% block modals %}{% endblock %}

<!-- After Bootstrap JS -->
{% block extra_js %}{% endblock %}
```

---

## File Structure Generated

```
inventory/
├── __init__.py
├── models.py          — Category, Supplier, Warehouse, Item, StockTransaction
├── views.py           — All views (dashboard, items, transactions, suppliers, warehouses, categories)
├── urls.py            — All URL patterns
├── admin.py           — Django admin registration
└── templates/
    └── inventory/
        ├── dashboard.html        — Inventory home with stats & alerts
        ├── item_list.html        — Item table with filters
        ├── item_form.html        — Add / Edit item form
        ├── item_detail.html      — Item detail + quick stock entry + history
        ├── stock_transaction.html — Stock In/Out log + new transaction modal
        ├── supplier_list.html    — Supplier management
        ├── warehouse_list.html   — Warehouse management
        └── category_list.html    — Category management
```

## Features Included

- Dashboard with live stats (total items, low stock count, stock value)
- Low stock alerts panel
- Recent transactions feed
- Item management (Add / Edit / Soft Delete)
- Stock In / Stock Out / Adjustment transactions
- Batch number & reference number tracking
- Per-item transaction history
- Supplier management (Add / Edit / Delete)
- Warehouse / location management
- Category management (Raw Material / Finished / Machinery)
- Unit of measurement (kg, ton, pcs, meters, litre, box)
- Search & filter on item list
- All modals use the fixed pattern ({% block modals %} outside content)
