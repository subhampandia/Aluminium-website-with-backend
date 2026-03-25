from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('order/', views.place_order, name='place_order'),
    path('order/products/', views.get_products_json, name='order_products_json'),

    # Backend — Orders
    path('manage/orders/', views.order_list, name='order_list'),
    path('manage/orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('manage/orders/<int:pk>/status/', views.update_order_status, name='order_update_status'),
    path('manage/orders/<int:pk>/invoice/', views.order_invoice_pdf, name='order_invoice'),

    # Backend — Products
    path('manage/products/', views.product_list, name='order_product_list'),
    path('manage/products/save/', views.product_save, name='order_product_save'),
    path('manage/products/<int:pk>/delete/', views.product_delete, name='order_product_delete'),
]
