from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Category(models.Model):
    CATEGORY_TYPES = [
        ('RAW', 'Raw Material'),
        ('FINISHED', 'Finished Product'),
        ('MACHINERY', 'Machinery & Spare Parts'),
    ]
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kilogram (kg)'),
        ('ton', 'Ton'),
        ('pcs', 'Pieces (pcs)'),
        ('mtr', 'Meters (mtr)'),
        ('ltr', 'Litre (ltr)'),
        ('box', 'Box'),
    ]

    name = models.CharField(max_length=200)
    item_code = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pcs')
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    low_stock_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=10)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item_code} - {self.name}"

    @property
    def is_low_stock(self):
        return self.current_stock <= self.low_stock_threshold

    @property
    def stock_value(self):
        return self.current_stock * self.purchase_price


class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJUST', 'Adjustment'),
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    batch_number = models.CharField(max_length=100, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    transaction_date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.item.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        if not self.pk:
            qty = self.quantity

            if self.transaction_type == 'IN':
                self.item.current_stock += qty

            elif self.transaction_type == 'OUT':
                if self.item.current_stock < qty:
                    raise ValueError("Not enough stock")
                self.item.current_stock -= qty

            elif self.transaction_type == 'ADJUST':
                self.item.current_stock = qty

            self.item.save()

        super().save(*args, **kwargs)
