from django.contrib import admin
from .models import Category, Supplier, Warehouse, Item, StockTransaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type']
    list_filter = ['category_type']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'email']
    search_fields = ['name', 'contact_person']


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'location']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['item_code', 'name', 'category', 'current_stock', 'unit', 'purchase_price', 'is_active']
    list_filter = ['category', 'is_active', 'warehouse']
    search_fields = ['name', 'item_code']


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ['item', 'transaction_type', 'quantity', 'batch_number', 'created_by', 'created_at']
    list_filter = ['transaction_type']
    search_fields = ['item__name', 'batch_number', 'reference_number']
