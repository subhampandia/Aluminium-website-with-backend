from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.utils import timezone
from .models import Item, Category, Supplier, Warehouse, StockTransaction
from decimal import Decimal
import json


def is_admin_or_store_manager(user):
    if user.is_superuser:
        return True
    try:
        return user.employee_profile.role in ['STORE_MANAGER']
    except:
        return False


def inventory_access(user):
    return user.is_superuser or is_admin_or_store_manager(user)


# ── DASHBOARD ──

@login_required
@user_passes_test(inventory_access)
def inventory_dashboard(request):
    base_template = 'base_dashboard.html' if request.user.is_superuser else 'base_store.html'

    all_active_items = Item.objects.filter(is_active=True).select_related('category')

    total_items = all_active_items.count()
    low_stock_items_list = [i for i in all_active_items if i.is_low_stock]
    low_stock_count = len(low_stock_items_list)
    total_stock_value = sum(i.stock_value for i in all_active_items)

    recent_transactions = StockTransaction.objects.select_related('item', 'created_by').order_by('-created_at')[:10]

    categories = Category.objects.all()
    category_data = []
    for cat in categories:
        count = all_active_items.filter(category=cat).count()
        category_data.append({'name': cat.name, 'count': count, 'type': cat.category_type})

    context = {
        'base_template': base_template,
        'total_items': total_items,
        'low_stock_count': low_stock_count,
        'total_stock_value': total_stock_value,
        'recent_transactions': recent_transactions,
        'category_data': category_data,
        'low_stock_items': low_stock_items_list,
    }
    return render(request, 'inventory/dashboard.html', context)


# ── ITEMS ──

@login_required
@user_passes_test(inventory_access)
def item_list(request):
    base_template = 'base_dashboard.html' if request.user.is_superuser else 'base_store.html'

    items = Item.objects.filter(is_active=True).select_related('category', 'supplier', 'warehouse')

    # Filters
    category_id = request.GET.get('category')
    search = request.GET.get('search')
    stock_filter = request.GET.get('stock')

    if category_id:
        items = items.filter(category_id=category_id)
    if search:
        items = items.filter(Q(name__icontains=search) | Q(item_code__icontains=search))
    if stock_filter == 'low':
        items = [i for i in items if i.is_low_stock]

    categories = Category.objects.all()

    context = {
        'base_template': base_template,
        'items': items,
        'categories': categories,
        'selected_category': category_id,
        'search': search,
    }
    return render(request, 'inventory/item_list.html', context)


@login_required
@user_passes_test(inventory_access)
def item_add(request):
    base_template = 'base_dashboard.html' if request.user.is_superuser else 'base_store.html'

    if request.method == 'POST':
        try:
            item = Item(
                name=request.POST['name'],
                item_code=request.POST['item_code'],
                category_id=request.POST['category'],
                supplier_id=request.POST.get('supplier') or None,
                warehouse_id=request.POST.get('warehouse') or None,
                unit=request.POST['unit'],
                purchase_price=request.POST['purchase_price'],
                current_stock=request.POST.get('current_stock', 0),
                low_stock_threshold=request.POST['low_stock_threshold'],
                description=request.POST.get('description', ''),
            )
            item.save()
            messages.success(request, f'Item "{item.name}" added successfully.')
            return redirect('inventory_item_list')
        except Exception as e:
            messages.error(request, f'Error adding item: {e}')

    context = {
        'base_template': base_template,
        'categories': Category.objects.all(),
        'suppliers': Supplier.objects.all(),
        'warehouses': Warehouse.objects.all(),
        'units': Item.UNIT_CHOICES,
    }
    return render(request, 'inventory/item_form.html', context)


@login_required
@user_passes_test(inventory_access)
def item_edit(request, pk):
    base_template = 'base_dashboard.html' if request.user.is_superuser else 'base_store.html'
    item = get_object_or_404(Item, pk=pk)

    if request.method == 'POST':
        try:
            item.name = request.POST['name']
            item.item_code = request.POST['item_code']
            item.category_id = request.POST['category']
            item.supplier_id = request.POST.get('supplier') or None
            item.warehouse_id = request.POST.get('warehouse') or None
            item.unit = request.POST['unit']
            item.purchase_price = request.POST['purchase_price']
            item.low_stock_threshold = request.POST['low_stock_threshold']
            item.description = request.POST.get('description', '')
            item.save()
            messages.success(request, f'Item "{item.name}" updated successfully.')
            return redirect('inventory_item_list')
        except Exception as e:
            messages.error(request, f'Error updating item: {e}')

    context = {
        'base_template': base_template,
        'item': item,
        'categories': Category.objects.all(),
        'suppliers': Supplier.objects.all(),
        'warehouses': Warehouse.objects.all(),
        'units': Item.UNIT_CHOICES,
    }
    return render(request, 'inventory/item_form.html', context)


@login_required
@user_passes_test(inventory_access)
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.is_active = False
        item.save()
        messages.success(request, f'Item "{item.name}" deleted.')
    return redirect('inventory_item_list')


@login_required
@user_passes_test(inventory_access)
def item_detail(request, pk):
    base_template = 'base_dashboard.html' if request.user.is_superuser else 'base_store.html'
    item = get_object_or_404(Item, pk=pk)
    transactions = item.transactions.select_related('created_by').order_by('-created_at')[:20]

    context = {
        'base_template': base_template,
        'item': item,
        'transactions': transactions,
    }
    return render(request, 'inventory/item_detail.html', context)


# ── STOCK TRANSACTIONS ──

@login_required
@user_passes_test(inventory_access)
def stock_transaction(request):
    base_template = 'base_dashboard.html' if request.user.is_superuser else 'base_store.html'

    if request.method == 'POST':
        try:
            item = get_object_or_404(Item, pk=request.POST['item_id'])
            transaction_type = request.POST['transaction_type']
            quantity = Decimal(request.POST['quantity'])

            if transaction_type == 'OUT' and item.current_stock < quantity:
                return JsonResponse({'success': False, 'message': f'Insufficient stock. Available: {item.current_stock} {item.unit}'})

            txn = StockTransaction(
                item=item,
                transaction_type=transaction_type,
                quantity=quantity,
                batch_number=request.POST.get('batch_number', ''),
                reference_number=request.POST.get('reference_number', ''),
                purchase_price=request.POST.get('purchase_price', item.purchase_price),
                notes=request.POST.get('notes', ''),
                created_by=request.user,
            )
            txn.save()

            return JsonResponse({
                'success': True,
                'message': f'Stock {transaction_type} recorded successfully.',
                'new_stock': float(item.current_stock),
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    items = Item.objects.filter(is_active=True).order_by('name')
    transactions = StockTransaction.objects.select_related('item', 'created_by').order_by('-created_at')[:50]

    # Filters
    txn_type = request.GET.get('type')
    if txn_type:
        transactions = StockTransaction.objects.filter(transaction_type=txn_type).select_related('item', 'created_by').order_by('-created_at')[:50]

    context = {
        'base_template': base_template,
        'items': items,
        'transactions': transactions,
        'txn_type': txn_type,
    }
    return render(request, 'inventory/stock_transaction.html', context)


# ── SUPPLIERS ──

@login_required
@user_passes_test(inventory_access)
def supplier_list(request):
    base_template = 'base_dashboard.html' if request.user.is_superuser else 'base_store.html'
    suppliers = Supplier.objects.all()
    context = {'base_template': base_template, 'suppliers': suppliers}
    return render(request, 'inventory/supplier_list.html', context)


@login_required
@user_passes_test(inventory_access)
def supplier_save(request):
    if request.method == 'POST':
        pk = request.POST.get('supplier_id')
        if pk:
            supplier = get_object_or_404(Supplier, pk=pk)
        else:
            supplier = Supplier()
        supplier.name = request.POST['name']
        supplier.contact_person = request.POST.get('contact_person', '')
        supplier.phone = request.POST.get('phone', '')
        supplier.email = request.POST.get('email', '')
        supplier.address = request.POST.get('address', '')
        supplier.save()
        messages.success(request, 'Supplier saved successfully.')
    return redirect('inventory_supplier_list')


@login_required
@user_passes_test(inventory_access)
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted.')
    return redirect('inventory_supplier_list')


# ── WAREHOUSES ──

@login_required
@user_passes_test(inventory_access)
def warehouse_list(request):
    base_template = 'base_dashboard.html' if request.user.is_superuser else 'base_store.html'
    warehouses = Warehouse.objects.all()
    context = {'base_template': base_template, 'warehouses': warehouses}
    return render(request, 'inventory/warehouse_list.html', context)


@login_required
@user_passes_test(inventory_access)
def warehouse_save(request):
    if request.method == 'POST':
        pk = request.POST.get('warehouse_id')
        if pk:
            warehouse = get_object_or_404(Warehouse, pk=pk)
        else:
            warehouse = Warehouse()
        warehouse.name = request.POST['name']
        warehouse.location = request.POST.get('location', '')
        warehouse.description = request.POST.get('description', '')
        warehouse.save()
        messages.success(request, 'Warehouse saved successfully.')
    return redirect('inventory_warehouse_list')


@login_required
@user_passes_test(inventory_access)
def warehouse_delete(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        warehouse.delete()
        messages.success(request, 'Warehouse deleted.')
    return redirect('inventory_warehouse_list')


# ── CATEGORIES ──

@login_required
@user_passes_test(inventory_access)
def category_list(request):
    base_template = 'base_dashboard.html' if request.user.is_superuser else 'base_store.html'
    categories = Category.objects.all()
    context = {'base_template': base_template, 'categories': categories}
    return render(request, 'inventory/category_list.html', context)


@login_required
@user_passes_test(inventory_access)
def category_save(request):
    if request.method == 'POST':
        pk = request.POST.get('category_id')
        if pk:
            category = get_object_or_404(Category, pk=pk)
        else:
            category = Category()
        category.name = request.POST['name']
        category.category_type = request.POST['category_type']
        category.description = request.POST.get('description', '')
        category.save()
        messages.success(request, 'Category saved successfully.')
    return redirect('inventory_category_list')


@login_required
@user_passes_test(inventory_access)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted.')
    return redirect('inventory_category_list')


# ── AJAX ──

@login_required
def get_item_stock(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return JsonResponse({
        'current_stock': float(item.current_stock),
        'unit': item.unit,
        'purchase_price': float(item.purchase_price),
        'is_low_stock': item.is_low_stock,
    })
