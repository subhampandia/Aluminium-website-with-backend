# Orders Module — Setup Instructions

## 1. Copy the app
Drop the `orders/` folder into your Django project root.

## 2. settings.py
```python
INSTALLED_APPS = [
    ...
    'inventory',  # must be installed first
    'orders',
]

# Email settings (for confirmation emails)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your@email.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
DEFAULT_FROM_EMAIL = 'AlumTech Industries <your@email.com>'
```

## 3. urls.py (main)
```python
urlpatterns = [
    ...
    path('', include('orders.urls')),  # puts /order/ at root level
]
```

## 4. Migrate
```bash
python manage.py makemigrations orders
python manage.py migrate
```

## 5. Add sidebar links for admin
In sidebar_admin.html, add under Orders section:

```html
<div class="sidebar-heading">Orders</div>

<a href="{% url 'order_list' %}"
   class="{% if '/manage/orders' in request.path %}active{% endif %}">
    <i class="bi bi-bag"></i>
    <span>Orders</span>
</a>

<a href="{% url 'order_product_list' %}"
   class="{% if '/manage/products' in request.path %}active{% endif %}">
    <i class="bi bi-boxes"></i>
    <span>Order Products</span>
</a>
```

Do the same for sidebar_store.html.

## 6. Update landing page
Replace the #products section in your landing page HTML
with the contents of LANDING_PAGE_PRODUCTS_SECTION.html

## 7. Add products in backend
Go to /manage/products/ and add products, linking each
to its corresponding inventory item for stock deduction.

## 8. Fix base_template in views.py
In orders/views.py, the _get_base() function uses:
- 'base_admin.html' for superuser
- 'base_store.html' for store manager
- 'base_accounts.html' for accounts

Update these to match your actual filenames.

---

## URL Summary
- /order/                    → Public order form (landing page link)
- /order/products/           → AJAX product list (used by order form)
- /manage/orders/            → Admin order list
- /manage/orders/<id>/       → Order detail + status update
- /manage/orders/<id>/invoice/ → Printable PDF invoice
- /manage/products/          → Manage orderable products

## Flow
1. Customer visits /order/ from landing page
2. Selects products, fills address, submits
3. Stock is auto-deducted from inventory
4. Customer gets confirmation email
5. Admin/Store Manager sees order in /manage/orders/
6. Admin updates status (Confirmed → Processing → Dispatched → Delivered)
7. Admin can print/download invoice from order detail page
