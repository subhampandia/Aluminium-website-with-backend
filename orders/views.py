from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from decimal import Decimal
import json

from .models import Order, OrderItem, Product
from inventory.models import Item, StockTransaction


def staff_access(user):
    if user.is_superuser:
        return True
    try:
        return user.employee_profile.role in ['HR', 'ACCOUNTS', 'STORE_MANAGER']
    except:
        return False


# ── PUBLIC: Place Order ──

def place_order(request):
    products = Product.objects.filter(is_active=True).order_by('category')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Collect order items from POST
                product_ids = request.POST.getlist('product_id[]')
                quantities = request.POST.getlist('quantity[]')

                if not product_ids:
                    return JsonResponse({'success': False, 'message': 'Please add at least one product.'})

                # Validate stock before creating order
                items_to_process = []
                for pid, qty in zip(product_ids, quantities):
                    if not pid or not qty:
                        continue
                    qty = Decimal(str(qty))
                    if qty <= 0:
                        continue
                    product = get_object_or_404(Product, pk=pid, is_active=True)

                    # Check inventory stock
                    if product.inventory_item:
                        if product.inventory_item.current_stock < qty:
                            return JsonResponse({
                                'success': False,
                                'message': f'Insufficient stock for "{product.name}". Available: {product.inventory_item.current_stock} {product.unit}'
                            })
                    items_to_process.append((product, qty))

                if not items_to_process:
                    return JsonResponse({'success': False, 'message': 'No valid items in order.'})

                # Create order
                order = Order(
                    customer_name=request.POST['customer_name'],
                    customer_email=request.POST['customer_email'],
                    customer_phone=request.POST['customer_phone'],
                    company_name=request.POST.get('company_name', ''),
                    address_line1=request.POST['address_line1'],
                    address_line2=request.POST.get('address_line2', ''),
                    city=request.POST['city'],
                    state=request.POST['state'],
                    pincode=request.POST['pincode'],
                    notes=request.POST.get('notes', ''),
                )
                order.save()

                total = Decimal('0')
                for product, qty in items_to_process:
                    item = OrderItem(
                        order=order,
                        product=product,
                        product_name=product.name,
                        quantity=qty,
                        unit=product.unit,
                        unit_price=product.price_per_unit,
                    )
                    item.save()
                    total += item.subtotal

                    # Auto-deduct from inventory
                    if product.inventory_item:
                        txn = StockTransaction(
                            item=product.inventory_item,
                            transaction_type='OUT',
                            quantity=qty,
                            reference_number=order.order_number,
                            notes=f'Order {order.order_number} — {order.customer_name}',
                        )
                        txn.save()

                order.total_amount = total
                order.save()

                # Send confirmation email
                try:
                    send_order_confirmation_email(order)
                except Exception as e:
                    pass  # Don't fail order if email fails

                return JsonResponse({
                    'success': True,
                    'message': 'Order placed successfully!',
                    'order_number': order.order_number,
                })

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    context = {'products': products}
    return render(request, 'orders/place_order.html', context)


def send_order_confirmation_email(order):
    subject = f'Order Confirmation — {order.order_number} | AlumTech Industries'
    message = render_to_string('orders/email_confirmation.html', {'order': order})
    send_mail(
        subject=subject,
        message='',
        html_message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.customer_email],
        fail_silently=True,
    )


# Replace the get_products_json function in orders/views.py with this:

def get_products_json(request):
    """AJAX endpoint to get products for order form"""
    products = Product.objects.filter(is_active=True).select_related('inventory_item')
    data = []
    for p in products:
        data.append({
            'id': p.id,
            'name': p.name,
            'category': p.category,
            'description': p.description,
            'unit': p.unit,
            'price_per_unit': str(p.price_per_unit),
            'min_order_qty': str(p.min_order_qty),
            'available_stock': float(p.inventory_item.current_stock) if p.inventory_item else None,
        })
    return JsonResponse({'products': data})



# ── BACKEND: Order Management ──

@login_required
@user_passes_test(staff_access)
def order_list(request):
    base_template = _get_base(request.user)
    orders = Order.objects.prefetch_related('items').all()

    # Filters
    status = request.GET.get('status')
    search = request.GET.get('search')

    if status:
        orders = orders.filter(status=status)
    if search:
        orders = orders.filter(
            order_number__icontains=search
        ) | orders.filter(
            customer_name__icontains=search
        ) | orders.filter(
            customer_email__icontains=search
        )

    # Stats
    stats = {
        'total': Order.objects.count(),
        'pending': Order.objects.filter(status='PENDING').count(),
        'confirmed': Order.objects.filter(status='CONFIRMED').count(),
        'dispatched': Order.objects.filter(status='DISPATCHED').count(),
    }

    context = {
        'base_template': base_template,
        'orders': orders,
        'stats': stats,
        'status_filter': status,
        'search': search,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'orders/order_list.html', context)


@login_required
@user_passes_test(staff_access)
def order_detail(request, pk):
    base_template = _get_base(request.user)
    order = get_object_or_404(Order, pk=pk)

    context = {
        'base_template': base_template,
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
@user_passes_test(staff_access)
def update_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            old_status = order.status
            order.status = new_status
            if new_status == 'CONFIRMED':
                order.confirmed_at = timezone.now()
            elif new_status == 'DISPATCHED':
                order.dispatched_at = timezone.now()
            order.save()
            messages.success(request, f'Order #{order.order_number} status updated to {order.get_status_display()}.')

    return redirect('order_detail', pk=pk)


@login_required
@user_passes_test(staff_access)
def order_invoice_pdf(request, pk):
    """Generate PDF invoice"""
    order = get_object_or_404(Order, pk=pk)

    try:
        from weasyprint import HTML
        html_string = render_to_string('orders/invoice_pdf.html', {'order': order})
        html = HTML(string=html_string)
        pdf = html.write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Invoice-{order.order_number}.pdf"'
        return response
    except ImportError:
        # Fallback: render printable HTML page
        return render(request, 'orders/invoice_pdf.html', {'order': order})


# ── PRODUCT MANAGEMENT ──

@login_required
@user_passes_test(staff_access)
def product_list(request):
    base_template = _get_base(request.user)
    products = Product.objects.select_related('inventory_item').all()
    from inventory.models import Item
    inventory_items = Item.objects.filter(is_active=True)
    context = {
        'base_template': base_template,
        'products': products,
        'inventory_items': inventory_items,
        'category_choices': Product.CATEGORY_CHOICES,
    }
    return render(request, 'orders/product_list.html', context)


@login_required
@user_passes_test(staff_access)
def product_save(request):
    if request.method == 'POST':
        pk = request.POST.get('product_id')
        if pk:
            product = get_object_or_404(Product, pk=pk)
        else:
            product = Product()

        product.name = request.POST['name']
        product.category = request.POST['category']
        product.description = request.POST['description']
        product.unit = request.POST['unit']
        product.price_per_unit = request.POST['price_per_unit']
        product.min_order_qty = request.POST.get('min_order_qty', 1)
        product.is_active = request.POST.get('is_active') == 'on'
        inv_item_id = request.POST.get('inventory_item')
        product.inventory_item_id = inv_item_id if inv_item_id else None
        product.save()
        messages.success(request, f'Product "{product.name}" saved.')
    return redirect('order_product_list')


@login_required
@user_passes_test(staff_access)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted.')
    return redirect('order_product_list')


def _get_base(user):
    if user.is_superuser:
        return 'base_dashboard.html'
    try:
        role = user.employee_profile.role
        if role == 'ACCOUNTS':
            return 'base_accounts_dashboard.html'
        if role == 'STORE_MANAGER':
            return 'base_store.html'
    except:
        pass
    return 'base.html'
