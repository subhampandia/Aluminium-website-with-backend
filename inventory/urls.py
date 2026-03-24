from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.inventory_dashboard, name='inventory_dashboard'),

    # Items
    path('items/', views.item_list, name='inventory_item_list'),
    path('items/add/', views.item_add, name='inventory_item_add'),
    path('items/<int:pk>/edit/', views.item_edit, name='inventory_item_edit'),
    path('items/<int:pk>/delete/', views.item_delete, name='inventory_item_delete'),
    path('items/<int:pk>/', views.item_detail, name='inventory_item_detail'),
    path('items/<int:pk>/stock/', views.get_item_stock, name='inventory_item_stock'),

    # Stock Transactions
    path('transactions/', views.stock_transaction, name='inventory_transactions'),

    # Suppliers
    path('suppliers/', views.supplier_list, name='inventory_supplier_list'),
    path('suppliers/save/', views.supplier_save, name='inventory_supplier_save'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='inventory_supplier_delete'),

    # Warehouses
    path('warehouses/', views.warehouse_list, name='inventory_warehouse_list'),
    path('warehouses/save/', views.warehouse_save, name='inventory_warehouse_save'),
    path('warehouses/<int:pk>/delete/', views.warehouse_delete, name='inventory_warehouse_delete'),

    # Categories
    path('categories/', views.category_list, name='inventory_category_list'),
    path('categories/save/', views.category_save, name='inventory_category_save'),
    path('categories/<int:pk>/delete/', views.category_delete, name='inventory_category_delete'),
]
