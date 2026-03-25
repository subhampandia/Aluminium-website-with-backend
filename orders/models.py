from django.db import models
from django.utils import timezone
from decimal import Decimal
import uuid


class Product(models.Model):
    """Public-facing products shown on landing page, linked to inventory items"""
    CATEGORY_CHOICES = [
        ('EXTRUSION', 'Aluminum Extrusions'),
        ('FABRICATION', 'Fabrication Services'),
        ('COMPONENTS', 'Industrial Components'),
        ('SHEETS', 'Aluminum Sheets & Plates'),
        ('FINISHING', 'Surface Finishing'),
        ('CUSTOM', 'Custom Solutions'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    unit = models.CharField(max_length=20, default='kg')
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    min_order_qty = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    is_active = models.BooleanField(default=True)

    # Link to inventory item for stock deduction
    inventory_item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='product'
    )

    def __str__(self):
        return self.name

    @property
    def available_stock(self):
        if self.inventory_item:
            return self.inventory_item.current_stock
        return None


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PROCESSING', 'Processing'),
        ('DISPATCHED', 'Dispatched'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False)

    # Customer Info
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    company_name = models.CharField(max_length=200, blank=True)

    # Delivery Address
    address_line1 = models.CharField(max_length=300)
    address_line2 = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    # Order Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    dispatched_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} — {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"AT-{timezone.now().strftime('%Y%m')}-{uuid.uuid4().hex[:5].upper()}"
        super().save(*args, **kwargs)

    @property
    def full_address(self):
        parts = [self.address_line1]
        if self.address_line2:
            parts.append(self.address_line2)
        parts += [self.city, self.state, self.pincode]
        return ', '.join(parts)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)  # snapshot
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = Decimal(str(self.quantity)) * Decimal(str(self.unit_price))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
